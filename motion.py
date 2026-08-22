import cv2


def detect_motion(frame, previous_frame, min_motion_area):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous_frame is None:
        return False, gray, []

    frame_difference = cv2.absdiff(previous_frame, gray)

    threshold = cv2.threshold(
        frame_difference,
        25,
        255,
        cv2.THRESH_BINARY
    )[1]

    threshold = cv2.dilate(
        threshold,
        None,
        iterations=2
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    motion = False
    boxes = []

    for contour in contours:

        if cv2.contourArea(contour) < min_motion_area:
            continue

        motion = True
        boxes.append(cv2.boundingRect(contour))

    return motion, gray, boxes
