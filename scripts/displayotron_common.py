#!/usr/bin/env python3
from __future__ import print_function

import json
import os


THEMES = [
    ("Blue", (0, 96, 160)),
    ("Green", (0, 140, 40)),
    ("Amber", (160, 90, 0)),
    ("White", (180, 180, 180)),
    ("Purple", (120, 40, 160)),
    ("Off", (0, 0, 0)),
]

SETTINGS_PATH = os.environ.get(
    "DISPLAYOTRON_SETTINGS_PATH",
    os.path.expanduser("~/.config/displayotron/settings.json"),
)


def clamp(value, low, high):
    return max(low, min(high, value))


def default_settings():
    return {
        "theme_index": 0,
        "brightness": 70,
        "contrast": 45,
        "status_service_enabled": True,
    }


def _coerce_bool(value, fallback):
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        token = value.strip().lower()
        if token in ("1", "true", "yes", "on"):
            return True
        if token in ("0", "false", "no", "off"):
            return False
    return fallback


def normalize_settings(data):
    settings = default_settings()
    if not isinstance(data, dict):
        return settings

    if "theme_index" in data:
        settings["theme_index"] = clamp(int(data["theme_index"]), 0, len(THEMES) - 1)
    if "brightness" in data:
        settings["brightness"] = clamp(int(data["brightness"]), 0, 100)
    if "contrast" in data:
        settings["contrast"] = clamp(int(data["contrast"]), 0, 63)
    if "status_service_enabled" in data:
        settings["status_service_enabled"] = _coerce_bool(
            data["status_service_enabled"],
            settings["status_service_enabled"],
        )

    return settings


def load_settings(path=None):
    settings_path = path or SETTINGS_PATH
    try:
        with open(settings_path, "r") as settings_file:
            data = json.load(settings_file)
    except (IOError, OSError, ValueError):
        return default_settings()

    try:
        return normalize_settings(data)
    except (TypeError, ValueError):
        return default_settings()


def save_settings(settings, path=None):
    settings_path = path or SETTINGS_PATH
    directory = os.path.dirname(settings_path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)

    with open(settings_path, "w") as settings_file:
        json.dump(normalize_settings(settings), settings_file, indent=2, sort_keys=True)


def theme_name(theme_index):
    return THEMES[clamp(int(theme_index), 0, len(THEMES) - 1)][0]


def apply_display(lcd, backlight, settings):
    normalized = normalize_settings(settings)
    base = THEMES[normalized["theme_index"]][1]

    scaled = []
    for value in base:
        scaled.append(int(value * normalized["brightness"] / 100.0))

    backlight.rgb(scaled[0], scaled[1], scaled[2])
    lcd.set_contrast(normalized["contrast"])
