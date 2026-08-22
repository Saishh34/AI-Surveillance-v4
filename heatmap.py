import cv2
import numpy as np

def create_heatmap(width, height):
    return np.zeros((height, width), dtype=np.float32)

def update_heatmap(heatmap, center_x, center_y, height, width, radius):
    heatmap[
        max(0, center_y - radius):min(height, center_y + radius),
        max(0, center_x - radius):min(width, center_x + radius)
    ] += 0.3

    heatmap *= 0.999



def render_heatmap(heatmap):
    """Build the colorized heatmap image without displaying it.

    Kept separate from draw_heatmap so background worker threads (as
    used by the multi-camera pipeline) can compute the image and hand
    it to the main thread to display, instead of calling cv2.imshow
    themselves.
    """
    heatmap_blur = cv2.GaussianBlur(
        heatmap,
        (31, 31),
        0
    )

    heatmap_display = cv2.normalize(
        heatmap_blur,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    ).astype(np.uint8)

    heatmap_color = cv2.applyColorMap(
        heatmap_display,
        cv2.COLORMAP_JET
    )

    return heatmap_color


def draw_heatmap(heatmap, window_name="AI Heatmap"):
    heatmap_color = render_heatmap(heatmap)
    cv2.imshow(window_name, heatmap_color)
