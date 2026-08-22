import os
import time
import threading
from datetime import datetime

import cv2

from ui import (
    draw_fps,
    draw_motion_status,
    draw_person_count,
    draw_timestamp,
    draw_intrusion_zone
)
from detector import create_detector, detect_people
from motion import detect_motion
from telegram_alert import send_telegram_photo
from heatmap import create_heatmap, update_heatmap, render_heatmap
from tracker import (
    create_track_history,
    draw_trail,
    handle_loitering,
    is_inside_zone
)
from recorder import (
    write_frame,
    release_writer,
    draw_recording_text,
    start_recording_if_needed
)
from zone_store import load_zone
import activity_log
import config


def _safe_folder_name(name):
    """Turn a camera display name into a filesystem-safe folder name."""
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)


class CameraWorker(threading.Thread):
    """
    Runs capture -> motion detection -> YOLO tracking -> intrusion /
    loitering logic -> heatmap -> recording -> Telegram alerts for a
    single camera, completely independently of any other camera.

    IMPORTANT: this thread never calls cv2.imshow / cv2.waitKey.
    OpenCV's HighGUI backend is not reliably thread-safe across
    platforms, so all display windows are owned and drawn by the main
    thread. Each worker just publishes its latest frames into
    `shared_frames[self.name]` for the main thread to pick up.
    """

    def __init__(self, name, camera_index, shared_frames, stop_event, zone=None):
        super().__init__(daemon=True)
        self.name = name
        self.camera_index = camera_index
        self.shared_frames = shared_frames
        self.stop_event = stop_event

        self.zone_x1, self.zone_y1, self.zone_x2, self.zone_y2 = self._resolve_zone(zone)

        self.recording_folder = os.path.join(
            config.RECORDING_FOLDER, _safe_folder_name(name)
        )
        self.snapshot_folder = os.path.join(
            config.SNAPSHOT_FOLDER, _safe_folder_name(name)
        )
        os.makedirs(self.recording_folder, exist_ok=True)
        os.makedirs(self.snapshot_folder, exist_ok=True)

        # Each worker owns its own YOLO model instance. Sharing a
        # single model between threads corrupts ByteTrack's internal
        # per-stream tracking state.
        self.model = create_detector(config.YOLO_MODEL)

        self.camera = None
        self.width = 0
        self.height = 0

    # -------------------------------------------------
    # Setup
    # -------------------------------------------------

    def _resolve_zone(self, zone):
        """
        Zone priority: zones.json (drawn via zone_selector.py) >
        per-camera override passed in via config.CAMERAS > global
        config default.
        """
        stored_zone = load_zone(self.name)

        if stored_zone:
            return stored_zone["x1"], stored_zone["y1"], stored_zone["x2"], stored_zone["y2"]

        zone = zone or {}
        return (
            zone.get("x1", config.ZONE_X1),
            zone.get("y1", config.ZONE_Y1),
            zone.get("x2", config.ZONE_X2),
            zone.get("y2", config.ZONE_Y2),
        )

    def _new_run_state(self):
        """
        Bundles all the per-run mutable state (recording status,
        track history, loitering timers, the heatmap array, etc.) into
        one dict instead of a long list of loose local variables, so
        it can be threaded through the helper methods below.
        """
        return {
            "previous_frame": None,
            "previous_time": time.time(),
            "video_writer": None,
            "recording": False,
            "intrusion": False,
            "last_detection_time": 0,
            "first_detection_time": 0,
            "snapshot1_taken": False,
            "snapshot2_taken": False,
            "track_history": create_track_history(),
            "entry_times": {},
            "loiter_alert_sent": {},
            "heatmap": create_heatmap(self.width, self.height),
        }

    # -------------------------------------------------
    # Main loop
    # -------------------------------------------------

    def run(self):
        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            print(f"[{self.name}] Cannot open camera (index {self.camera_index}).")
            self.shared_frames[self.name] = {"error": "camera not available"}
            return

        self.width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"[{self.name}] Started - {self.width}x{self.height} (index {self.camera_index})")

        state = self._new_run_state()

        while not self.stop_event.is_set():

            ret, frame = self.camera.read()

            if not ret:
                print(f"[{self.name}] Failed to capture frame.")
                break

            self._process_frame(frame, state)

        self._cleanup(state)

    def _process_frame(self, frame, state):
        display = frame.copy()
        fps = self._compute_fps(state)

        motion_detected, gray, motion_boxes = detect_motion(
            frame, state["previous_frame"], config.MIN_MOTION_AREA
        )
        state["previous_frame"] = gray

        for (x, y, w, h) in motion_boxes:
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

        person_count = 0
        state["intrusion"] = False

        if motion_detected:
            display, person_count = self._run_detection(frame, display, state)

        draw_fps(display, fps)
        draw_motion_status(display, motion_detected)
        draw_person_count(display, person_count)
        draw_timestamp(display, datetime.now().strftime("%d-%m-%Y %H:%M:%S"), self.height)

        self._handle_active_recording(frame, display, state)

        # Publish the latest frames for the main thread to display.
        # Plain dict assignment is atomic under the GIL, so no lock
        # is needed here.
        self.shared_frames[self.name] = {
            "display": display,
            "heatmap": render_heatmap(state["heatmap"]),
            "fps": fps,
            "motion_detected": motion_detected,
            "person_count": person_count,
            "intrusion": state["intrusion"] if motion_detected else False,
            "recording": state["recording"],
        }

    @staticmethod
    def _compute_fps(state):
        now = time.time()
        elapsed = now - state["previous_time"]
        state["previous_time"] = now
        return 1 / elapsed if elapsed > 0 else 0.0

    # -------------------------------------------------
    # YOLO detection / tracking / zone logic
    # -------------------------------------------------

    def _run_detection(self, frame, display, state):
        results = detect_people(
            self.model, frame, "bytetrack.yaml", config.YOLO_IMAGE_SIZE
        )

        display = results[0].plot()
        person_count = len(results[0].boxes)

        intrusion = False

        for box in results[0].boxes:
            if box.id is None:
                continue

            if self._process_track_box(box, display, frame, state):
                intrusion = True

        state["intrusion"] = intrusion

        self._handle_intrusion(display, intrusion, frame, person_count, state)

        return display, person_count

    def _process_track_box(self, box, display, frame, state):
        """Handles one tracked person for this frame. Returns True if
        this person is inside the intrusion zone."""
        track_id = int(box.id.item())
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        update_heatmap(
            state["heatmap"], center_x, center_y, self.height, self.width, config.HEAT_RADIUS
        )
        draw_trail(display, state["track_history"], track_id, center_x, center_y)

        heat_value = state["heatmap"][center_y, center_x]
        cv2.putText(
            display, f"Heat: {heat_value:.1f}", (x1, y1 - 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2
        )

        inside_zone = is_inside_zone(
            center_x, center_y, self.zone_x1, self.zone_y1, self.zone_x2, self.zone_y2
        )

        entry_times = state["entry_times"]
        loiter_alert_sent = state["loiter_alert_sent"]

        if inside_zone:
            # Log exactly once per visit - right as the track first
            # enters the zone, not every frame it stays there - so
            # the activity log tracks "how many visits", not "how
            # many frames".
            is_new_entry = track_id not in entry_times

            handle_loitering(
                display, track_id, x1, y2,
                entry_times, loiter_alert_sent, config.LOITER_TIME
            )

            if is_new_entry:
                self._log_zone_entry(frame)
        else:
            entry_times.pop(track_id, None)
            loiter_alert_sent.pop(track_id, None)

        return inside_zone

    def _handle_intrusion(self, display, intrusion, frame, person_count, state):
        if intrusion and state["first_detection_time"] == 0:
            state["first_detection_time"] = time.time()

        elapsed = (
            time.time() - state["first_detection_time"]
            if state["first_detection_time"] else 0
        )

        draw_intrusion_zone(display, self.zone_x1, self.zone_y1, self.zone_x2, self.zone_y2)

        if not intrusion:
            return

        if elapsed >= 0.5 and not state["snapshot1_taken"]:
            self._take_snapshot(frame, person_count, suffix="")
            state["snapshot1_taken"] = True

        if elapsed >= 1.5 and not state["snapshot2_taken"]:
            self._take_snapshot(frame, person_count, suffix="_2")
            state["snapshot2_taken"] = True

        state["last_detection_time"] = time.time()

        state["recording"], state["video_writer"] = start_recording_if_needed(
            state["recording"], state["video_writer"], self.recording_folder,
            self.width, self.height, config.VIDEO_FPS
        )

    # -------------------------------------------------
    # Recording
    # -------------------------------------------------

    def _handle_active_recording(self, frame, display, state):
        if not state["recording"]:
            return

        write_frame(state["video_writer"], frame)
        draw_recording_text(display, self.width)

        if time.time() - state["last_detection_time"] > config.RECORD_AFTER_DETECTION:
            state["recording"] = False
            state["first_detection_time"] = 0
            state["snapshot1_taken"] = False
            state["snapshot2_taken"] = False
            release_writer(state["video_writer"])
            state["video_writer"] = None
            print(f"[{self.name}] Recording Saved")

    def _cleanup(self, state):
        release_writer(state["video_writer"])
        self.camera.release()
        self.shared_frames.pop(self.name, None)
        print(f"[{self.name}] Stopped")

    # -------------------------------------------------
    # Behavioral anomaly detection
    # -------------------------------------------------

    def _log_zone_entry(self, frame):
        """
        Records this zone visit in the persistent activity log and
        checks it against the historical baseline for this camera and
        hour of day. If it's flagged as unusual, fires a separate,
        higher-priority alert on top of the normal intrusion snapshot.
        """
        now = datetime.now()
        activity_log.log_event(self.name, now)

        is_anomaly, reason, baseline_avg, days_monitored = activity_log.check_anomaly(
            self.name, now
        )

        if is_anomaly:
            self._send_anomaly_alert(frame, reason, baseline_avg, days_monitored)
        else:
            print(f"[{self.name}] Zone entry logged (hour {now.hour}) - {reason}")

    # -------------------------------------------------
    # Alerts (shared dispatch to avoid duplicating the
    # save-snapshot + send-Telegram-photo logic)
    # -------------------------------------------------

    def _dispatch_alert(self, frame, filename_suffix, caption, log_label):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        snapshot_name = f"{timestamp}{filename_suffix}.jpg"
        snapshot_path = os.path.join(self.snapshot_folder, snapshot_name)

        cv2.imwrite(snapshot_path, frame)

        threading.Thread(
            target=send_telegram_photo,
            args=(snapshot_path, caption),
            daemon=True
        ).start()

        print(f"[{self.name}] {log_label} : {snapshot_name}")

    def _take_snapshot(self, frame, person_count, suffix):
        caption = (
            f"🚨 AI Surveillance Alert\n\n"
            f"📷 Camera: {self.name}\n"
            f"👤 Person Detected\n"
            f"👥 Persons: {person_count}\n"
            f"🕒 Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        )
        self._dispatch_alert(frame, suffix, caption, "Snapshot Saved")

    def _send_anomaly_alert(self, frame, reason, baseline_avg, days_monitored):
        caption = (
            f"⚠️ UNUSUAL ACTIVITY DETECTED\n\n"
            f"📷 Camera: {self.name}\n"
            f"🕒 Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
            f"📊 Reason: {reason}\n"
            f"📈 Usual activity this hour: ~{baseline_avg:.1f}/day "
            f"(based on {days_monitored} days of history)"
        )
        self._dispatch_alert(frame, "_ANOMALY", caption, "ANOMALY ALERT sent")
