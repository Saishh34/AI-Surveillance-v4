import cv2


def draw_fps(display, fps):
    cv2.putText(
        display,
        f"FPS : {fps:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


def draw_motion_status(display, motion_detected):
    status = "Motion Detected" if motion_detected else "No Motion"

    cv2.putText(
        display,
        status,
        (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )


def draw_person_count(display, count):
    cv2.putText(
        display,
        f"Persons : {count}",
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )


def draw_timestamp(display, text, height):
    cv2.putText(
        display,
        text,
        (10, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


def draw_intrusion_zone(display, x1, y1, x2, y2):
    cv2.rectangle(
        display,
        (x1, y1),
        (x2, y2),
        (0, 0, 255),
        2
    )

    cv2.putText(
        display,
        "INTRUSION ZONE",
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
    )
