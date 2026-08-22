"""
Quick helper to figure out which camera index maps to which physical
camera. Opens each index in turn, shows a preview window for a couple
seconds, then moves on. Note the order/labels you see and update
CAMERAS in config.py to match.

Usage: python list_cameras.py
"""

import cv2

MAX_INDEX_TO_CHECK = 5
PREVIEW_SECONDS = 3


def main():
    found = []

    for index in range(MAX_INDEX_TO_CHECK):
        camera = cv2.VideoCapture(index)

        if not camera.isOpened():
            camera.release()
            continue

        found.append(index)
        print(f"Camera index {index} opened. Showing preview for {PREVIEW_SECONDS}s...")

        start = cv2.getTickCount()
        freq = cv2.getTickFrequency()

        while (cv2.getTickCount() - start) / freq < PREVIEW_SECONDS:
            ret, frame = camera.read()

            if not ret:
                break

            cv2.putText(
                frame, f"Camera Index: {index}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
            )
            cv2.imshow("Camera Index Check", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()

    print("=" * 40)
    print(f"Working camera indices found: {found}")
    print("Update the 'index' values in config.py -> CAMERAS to match.")
    print("=" * 40)


if __name__ == "__main__":
    main()
