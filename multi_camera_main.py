import threading

import cv2

import config
import activity_log
from camera_worker import CameraWorker
from grid_display import build_grid
from shared_state import shared_frames

WINDOW_NAME = "AI Surveillance - Multi Camera"


def main():
    activity_log.init_db()

    
    stop_event = threading.Event()

    workers = [
        CameraWorker(
            name=cam["name"],
            camera_index=cam["index"],
            shared_frames=shared_frames,
            stop_event=stop_event,
            zone=cam.get("zone"),
        )
        for cam in config.CAMERAS
    ]

    for worker in workers:
        worker.start()

    print("=" * 40)
    print("AI Surveillance Started (Multi-Camera)")
    for cam in config.CAMERAS:
        print(f" - {cam['name']} (index {cam['index']})")
    print("Press 'q' to stop all cameras.")
    print("=" * 40)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:
        while True:
            # Build panels in a fixed order (feed, heatmap, feed,
            # heatmap...) so the grid stays stable even if a camera's
            # frames haven't arrived yet.
            panels = []

            for cam in config.CAMERAS:
                name = cam["name"]
                frames = shared_frames.get(name)

                if frames is None or "error" in frames:
                    panels.append((f"{name} (Feed)", None))
                    panels.append((f"{name} (Heatmap)", None))
                else:
                    panels.append((f"{name} (Feed)", frames["display"]))
                    panels.append((f"{name} (Heatmap)", frames["heatmap"]))

            grid = build_grid(panels)
            cv2.imshow(WINDOW_NAME, grid)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if not any(worker.is_alive() for worker in workers):
                print("All camera threads have stopped.")
                break

    finally:
        stop_event.set()

        for worker in workers:
            worker.join(timeout=5)

        cv2.destroyAllWindows()

        print("=" * 40)
        print("AI Surveillance Closed")
        print("=" * 40)


if __name__ == "__main__":
    main()
