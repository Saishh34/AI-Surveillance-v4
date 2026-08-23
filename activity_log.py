"""
Persistent activity log used for time-of-day anomaly detection.

Every time someone enters a camera's intrusion zone, one event is
logged here (once per visit, not per frame) with a timestamp. Over
multiple days this builds a picture of "when does this zone normally
see activity" per camera, per hour of day. New zone entries are then
compared against that history so you get a stronger alert when
activity happens at a genuinely unusual time (e.g. 3 AM, if that hour
has never seen activity before) or at an unusually high volume for
that hour.

This is deliberately separate from heatmap.py. The heatmap is a live,
short-term spatial visualization that resets every run and decays
within minutes - it has nothing to do with long-term time-of-day
patterns. This module is the part that actually remembers things
across days.

Needs at least config.MIN_DAYS_FOR_BASELINE distinct days of data per
camera before it will flag anything as anomalous - before that it
just logs quietly so it has something to compare against later.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, date

import config

DB_FILE = getattr(config, "ACTIVITY_LOG_FILE", "activity_log.db")


@contextmanager
def _connect():
    # A fresh connection per call keeps this safe to call from
    # multiple camera threads concurrently without sharing a
    # connection object across threads.
    conn = sqlite3.connect(DB_FILE, timeout=10)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_name TEXT NOT NULL,
                event_date TEXT NOT NULL,  -- 'YYYY-MM-DD', local time
                hour INTEGER NOT NULL,     -- 0-23, local time
                timestamp REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_camera_hour
            ON events (camera_name, hour)
        """)


def log_event(camera_name, when=None):
    when = when or datetime.now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO events (camera_name, event_date, hour, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (camera_name, when.strftime("%Y-%m-%d"), when.hour, when.timestamp())
        )


def _days_monitored(conn, camera_name):
    """
    Approximates how many distinct days this camera has been actively
    logging events for, using the distinct calendar dates present in
    its own event history. This slightly undercounts quiet days with
    zero events, which is an acceptable simplification for a home
    setup - it means the baseline is a bit conservative rather than
    diluted by days the system may not have even been running.
    """
    cur = conn.execute(
        "SELECT COUNT(DISTINCT event_date) FROM events WHERE camera_name = ?",
        (camera_name,)
    )
    return cur.fetchone()[0] or 0


def get_baseline(camera_name, hour, exclude_date=None):
    """
    Returns (avg_events_per_day, days_monitored) for this camera/hour,
    based on historical days excluding `exclude_date` (normally today,
    so today's still-accumulating count doesn't skew its own baseline).
    """
    with _connect() as conn:
        days_monitored = _days_monitored(conn, camera_name)

        if exclude_date:
            cur = conn.execute(
                "SELECT COUNT(*) FROM events "
                "WHERE camera_name = ? AND hour = ? AND event_date != ?",
                (camera_name, hour, exclude_date)
            )
        else:
            cur = conn.execute(
                "SELECT COUNT(*) FROM events WHERE camera_name = ? AND hour = ?",
                (camera_name, hour)
            )

        total_events = cur.fetchone()[0] or 0

    if days_monitored <= 0:
        return 0.0, 0

    return total_events / days_monitored, days_monitored


def count_today(camera_name, hour, today=None):
    today = today or date.today().strftime("%Y-%m-%d")
    with _connect() as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM events "
            "WHERE camera_name = ? AND hour = ? AND event_date = ?",
            (camera_name, hour, today)
        )
        return cur.fetchone()[0] or 0


def check_anomaly(camera_name, when=None):
    """
    Call this right after log_event() for a new zone entry. Returns
    (is_anomaly, reason, baseline_avg, days_monitored).
    """
    when = when or datetime.now()
    today = when.strftime("%Y-%m-%d")
    hour = when.hour

    baseline_avg, days_monitored = get_baseline(camera_name, hour, exclude_date=today)

    if days_monitored < config.MIN_DAYS_FOR_BASELINE:
        reason = f"still learning baseline ({days_monitored}/{config.MIN_DAYS_FOR_BASELINE} days)"
        return False, reason, baseline_avg, days_monitored

    today_count = count_today(camera_name, hour, today)

    if baseline_avg == 0:
        reason = "activity at a time this zone has never seen before"
        return True, reason, baseline_avg, days_monitored

    if today_count > baseline_avg * config.ANOMALY_MULTIPLIER:
        reason = (
            f"activity level today ({today_count}) far exceeds the usual "
            f"~{baseline_avg:.1f}/day for this hour"
        )
        return True, reason, baseline_avg, days_monitored

    return False, "within normal range", baseline_avg, days_monitored

def get_recent_events(limit=20):
    """
    Returns the most recent intrusion-zone events.
    """
    with _connect() as conn:
        cur = conn.execute(
            """
            SELECT id, camera_name, event_date, hour, timestamp
            FROM events
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "camera_name": row[1],
            "event_date": row[2],
            "hour": row[3],
            "timestamp": row[4],
        }
        for row in rows
    ]