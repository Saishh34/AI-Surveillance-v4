"""
Interactive intrusion-zone selector.

Opens a live feed from one of your configured cameras, lets you
click-and-drag a rectangle over the area you want treated as the
intrusion zone, and saves it to zones.json.

Usage:
    python zone_selector.py                 -> pick a camera from a menu
    python zone_selector.py "Laptop Camera"  -> jump straight to that camera
    python zone_selector.py 0                -> jump straight to camera index 0

Controls:
    Click + drag  - draw the zone rectangle
    s             - save the current rectangle and exit
    r             - clear the rectangle and start over
    q / Esc       - quit without saving
"""

import sys

import cv2

import config
from zone_store import save_zone, load_zone

WINDOW_NAME = "Zone Selector"

drawing = False
start_point = (0, 0)
current_rect = None  # (x1, y1, x2, y2) in display/frame coordinates


def _normalize(rect):
    x1, y1, x2, y2 = rect
    return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def _mouse_callback(event, x, y, flags, param):
    global drawing, start_point, current_rect

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        current_rect = (x, y, x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            current_rect = (start_point[0], start_point[1], x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        current_rect = _normalize((start_point[0], start_point[1], x, y))


def _pick_camera():
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Allow passing a raw camera index directly.
        if arg.isdigit():
            index = int(arg)
            for cam in config.CAMERAS:
                if cam["index"] == index:
                    return cam
            return {"name": f"Camera {index}", "index": index}

        # Otherwise match by name.
        for cam in config.CAMERAS:
            if cam["name"].lower() == arg.lower():
                return cam

        print(f"No camera named '{arg}' found in config.CAMERAS.")
        sys.exit(1)

    if not config.CAMERAS:
        print("config.CAMERAS is empty - nothing to select a zone for.")
        sys.exit(1)

    if len(config.CAMERAS) == 1:
        return config.CAMERAS[0]

    print("Select a camera:")
    for i, cam in enumerate(config.CAMERAS):
        print(f"  [{i}] {cam['name']} (index {cam['index']})")

    choice = input("Enter number: ").strip()

    try:
        return config.CAMERAS[int(choice)]
    except (ValueError, IndexError):
        print("Invalid choice.")
        sys.exit(1)


def main():
    global current_rect

    cam = _pick_camera()
    name, index = cam["name"], cam["index"]

    camera = cv2.VideoCapture(index)

    if not camera.isOpened():
        print(f"Cannot open camera '{name}' (index {index}).")
        sys.exit(1)

    # Pre-load any existing zone for this camera so you're adjusting
    # it rather than starting from scratch.
    existing = load_zone(name)
    if existing:
        current_rect = (existing["x1"], existing["y1"], existing["x2"], existing["y2"])
        print(f"Loaded existing zone for '{name}': {existing}")

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, _mouse_callback)

    print("=" * 50)
    print(f"Setting intrusion zone for: {name}")
    print("Drag to draw the zone. Press 's' to save, 'r' to reset, 'q' to quit.")
    print("=" * 50)

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Failed to read from camera.")
            break

        display = frame.copy()

        if current_rect:
            x1, y1, x2, y2 = current_rect
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                display, f"({x1},{y1}) - ({x2},{y2})", (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2
            )

        cv2.rectangle(display, (0, 0), (display.shape[1], 50), (0, 0, 0), -1)
        cv2.putText(
            display, "Drag to draw zone | s=save  r=reset  q=quit", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA
        )

        cv2.imshow(WINDOW_NAME, display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            if current_rect is None:
                print("No rectangle drawn yet - drag on the video first.")
                continue

            x1, y1, x2, y2 = _normalize(current_rect)

            if x2 - x1 < 5 or y2 - y1 < 5:
                print("Rectangle too small - draw a proper zone first.")
                continue

            saved = save_zone(name, x1, y1, x2, y2)
            print(f"Saved zone for '{name}': {saved}")
            print("The running surveillance system will pick this up next time it starts.")
            break

        elif key == ord("r"):
            current_rect = None

        elif key in (ord("q"), 27):  # 'q' or Esc
            print("Quit without saving.")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
