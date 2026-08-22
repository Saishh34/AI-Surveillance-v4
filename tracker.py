import time
from collections import defaultdict

import cv2


def create_track_history():
    return defaultdict(list)


def draw_trail(display, track_history, track_id, center_x, center_y):

    track_history[track_id].append((center_x, center_y))

    # Keep only the last 50 points
    if len(track_history[track_id]) > 50:
        track_history[track_id].pop(0)

    points = track_history[track_id]

    for i in range(1, len(points)):
        cv2.line(
            display,
            points[i - 1],
            points[i],
            (255, 0, 255),
            2
        )


def handle_loitering(
    display,
    track_id,
    x1,
    y2,
    entry_times,
    loiter_alert_sent,
    loiter_time
):
    if track_id not in entry_times:
        entry_times[track_id] = time.time()
        loiter_alert_sent[track_id] = False

    stay_time = time.time() - entry_times[track_id]

    cv2.putText(
        display,
        f"{stay_time:.1f}s",
        (x1, y2 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2
    )

    if stay_time >= loiter_time and not loiter_alert_sent[track_id]:
        print(f"Loitering detected! Person {track_id}")
        loiter_alert_sent[track_id] = True


def is_inside_zone(
    center_x,
    center_y,
    x1,
    y1,
    x2,
    y2
):
    return (
        x1 <= center_x <= x2 and
        y1 <= center_y <= y2
    )
