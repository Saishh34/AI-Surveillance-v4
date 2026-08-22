import os
from datetime import datetime

import cv2


def create_video_writer(filepath, width, height, fps):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    return cv2.VideoWriter(
        filepath,
        fourcc,
        fps,
        (width, height)
    )


def write_frame(video_writer, frame):
    if video_writer is not None:
        video_writer.write(frame)


def release_writer(video_writer):
    if video_writer is not None:
        video_writer.release()


def create_recording_path(folder, filename):
    return os.path.join(folder, filename)


def draw_recording_text(display, width):
    cv2.putText(
        display,
        "RECORDING",
        (width - 190, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )


def generate_recording_filename():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S.mp4")


def start_recording(filepath, width, height, fps):
    video_writer = create_video_writer(
        filepath,
        width,
        height,
        fps
    )

    print(f"Recording Started : {os.path.basename(filepath)}")

    return video_writer


def start_recording_if_needed(
    recording,
    video_writer,
    recording_folder,
    width,
    height,
    fps
):
    if recording:
        return recording, video_writer

    filename = generate_recording_filename()

    filepath = create_recording_path(
        recording_folder,
        filename
    )

    video_writer = start_recording(
        filepath,
        width,
        height,
        fps
    )

    return True, video_writer
