import os
from dotenv import load_dotenv

load_dotenv()
# =====================================================
# Camera Settings
# =====================================================
# -------------------------
# Multi-Camera Settings
# -------------------------
# "index" is the OS camera index. On most laptops the built-in webcam
# is 0 and the first external USB webcam (e.g. Intex) is 1.
# If the external camera doesn't show up as 1, run list_cameras.py
# (created alongside this feature) to find the correct index.
#
# "zone" is optional - omit it (or set to None) to use the global
# ZONE_X1..ZONE_Y2 intrusion zone defined below for that camera.
CAMERAS = [
    {
        "name": "External Camera (Intex)",
        "index": 0,
        "zone": None,
    },
    {
        "name": "Laptop Camera",
        "index": 1,
        "zone": None,
    },
]

VIDEO_FPS = 20
RECORD_AFTER_DETECTION = 5

# =====================================================
# Folders
# =====================================================

RECORDING_FOLDER = "recordings"
SNAPSHOT_FOLDER = "snapshots"

# =====================================================
# YOLO
# =====================================================

YOLO_MODEL = "yolo11n.pt"

YOLO_IMAGE_SIZE = 320

# =====================================================
# Intrusion Zone
# =====================================================

ZONE_X1 = 150
ZONE_Y1 = 220

ZONE_X2 = 520
ZONE_Y2 = 470

# =====================================================
# Loitering
# =====================================================

LOITER_TIME = 15

# =====================================================
# Heatmap
# =====================================================

HEAT_RADIUS = 20
HEAT_DECAY = 0.999

# =====================================================
# Multi-Camera Grid Display
# =====================================================
# Size of each tile in the combined grid window. Bigger tiles = less
# downscaling = sharper heatmap/feed image, but a bigger window.
# Matching your camera's actual capture resolution avoids downscaling
# entirely, which gives the sharpest possible result.
GRID_CELL_WIDTH = 640
GRID_CELL_HEIGHT = 480

# =====================================================
# Behavioral Anomaly Detection
# =====================================================
# Every zone entry gets logged (camera, timestamp) to this SQLite file.
# Over time this builds a picture of "when does this zone normally see
# activity" per camera, per hour of day (0-23). New entries are then
# compared against that history.
ACTIVITY_LOG_FILE = "activity_log.db"

# Minimum distinct days of history required before anomaly flags turn
# on. Below this, entries are still logged (to build the baseline) but
# nothing gets flagged as unusual yet.
MIN_DAYS_FOR_BASELINE = 3

# An hour's activity today is flagged as anomalous if it exceeds the
# historical average for that hour by this multiplier (or if that hour
# has never seen any activity in the historical data at all).
ANOMALY_MULTIPLIER = 3

# =====================================================
# Motion Detection
# =====================================================

MIN_MOTION_AREA = 1000

# =====================================================
# Telegram
# =====================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

