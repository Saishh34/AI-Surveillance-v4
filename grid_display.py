import math

import cv2
import numpy as np

import config

# Size each panel gets resized to inside the grid. Configurable in
# config.py (GRID_CELL_WIDTH / GRID_CELL_HEIGHT) - matching your
# camera's native capture resolution avoids downscaling entirely,
# which gives the sharpest result, especially for the heatmap's soft
# gradients.
CELL_WIDTH = getattr(config, "GRID_CELL_WIDTH", 640)
CELL_HEIGHT = getattr(config, "GRID_CELL_HEIGHT", 480)

LABEL_BAR_HEIGHT = 28
LABEL_COLOR = (255, 255, 255)
LABEL_BG_COLOR = (0, 0, 0)


def _resize_for_panel(frame, target_w, target_h):
    """
    Resize with the interpolation method that best preserves quality
    for the direction we're scaling in. INTER_AREA avoids the
    blocky/aliased look that the default resize produces when
    shrinking (which is especially visible on the heatmap's smooth
    gradients); INTER_LINEAR (technically INTER_CUBIC for a sharper
    result) is used when enlarging.
    """
    h, w = frame.shape[:2]

    if target_w < w or target_h < h:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC

    return cv2.resize(frame, (target_w, target_h), interpolation=interpolation)


def _make_panel(frame, label):
    """Resize a frame to the fixed cell size and stamp a label on it."""
    if frame is None:
        panel = np.zeros((CELL_HEIGHT, CELL_WIDTH, 3), dtype=np.uint8)
        cv2.putText(
            panel, "No Signal", (20, CELL_HEIGHT // 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2
        )
    else:
        panel = _resize_for_panel(frame, CELL_WIDTH, CELL_HEIGHT)

    cv2.rectangle(panel, (0, 0), (CELL_WIDTH, LABEL_BAR_HEIGHT), LABEL_BG_COLOR, -1)
    cv2.putText(
        panel, label, (8, LABEL_BAR_HEIGHT - 8),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, LABEL_COLOR, 1, cv2.LINE_AA
    )

    return panel


def build_grid(panels):
    """
    Compose a list of (label, frame) tuples into one square-ish grid
    image. `frame` may be None to render a "No Signal" placeholder
    tile (e.g. a camera that failed to open).
    """
    if not panels:
        return np.zeros((CELL_HEIGHT, CELL_WIDTH, 3), dtype=np.uint8)

    count = len(panels)
    cols = math.ceil(math.sqrt(count))
    rows = math.ceil(count / cols)

    canvas = np.zeros((rows * CELL_HEIGHT, cols * CELL_WIDTH, 3), dtype=np.uint8)

    for index, (label, frame) in enumerate(panels):
        row = index // cols
        col = index % cols

        panel = _make_panel(frame, label)

        y0, y1 = row * CELL_HEIGHT, (row + 1) * CELL_HEIGHT
        x0, x1 = col * CELL_WIDTH, (col + 1) * CELL_WIDTH

        canvas[y0:y1, x0:x1] = panel

    return canvas
