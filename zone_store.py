"""
Shared helper for reading/writing per-camera intrusion zones.

Zones drawn with zone_selector.py are stored here, keyed by camera
name (must match the "name" field in config.py -> CAMERAS). This file
is read by camera_worker.py at startup and takes priority over any
zone hardcoded in config.py.
"""

import json
import os

ZONES_FILE = "zones.json"


def load_all_zones():
    if not os.path.exists(ZONES_FILE):
        return {}

    try:
        with open(ZONES_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print(f"Warning: could not read {ZONES_FILE}, ignoring it.")
        return {}


def load_zone(camera_name):
    """Returns {'x1':.., 'y1':.., 'x2':.., 'y2':..} or None if unset."""
    return load_all_zones().get(camera_name)


def save_zone(camera_name, x1, y1, x2, y2):
    zones = load_all_zones()

    zones[camera_name] = {
        "x1": int(x1),
        "y1": int(y1),
        "x2": int(x2),
        "y2": int(y2),
    }

    with open(ZONES_FILE, "w") as f:
        json.dump(zones, f, indent=2)

    return zones[camera_name]
