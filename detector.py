from ultralytics import YOLO


def create_detector(model_path):
    return YOLO(model_path)


def detect_people(
    model,
    frame,
    tracker_file,
    image_size
):
    results = model.track(
        frame,
        persist=True,
        tracker=tracker_file,
        classes=[0],
        imgsz=image_size,
        verbose=False
    )

    return results
