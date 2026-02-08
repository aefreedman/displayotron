#!/usr/bin/python3
from __future__ import print_function

import argparse
import subprocess
import sys
import time

import dothat.backlight as backlight
import dothat.lcd as lcd

sys.path.insert(0, "/usr/local/bin")

try:
    from displayotron_common import load_settings
    from displayotron_common import THEMES
    from displayotron_common import normalize_settings
except Exception:
    load_settings = None
    THEMES = []
    normalize_settings = None


SERVICE_NAME = "displayotron-status"
SAFE_LCD_ASCII = set(chr(code) for code in range(32, 127))


def fit(text):
    return str(text)[:16].ljust(16)


def sanitize_lcd_text(value):
    text = " ".join(str(value).split())
    sanitized = []
    for char in text:
        if char in SAFE_LCD_ASCII:
            sanitized.append(char)
        else:
            sanitized.append("?")
    return "".join(sanitized)


def run_quiet(command):
    with open("/dev/null", "w") as devnull:
        return subprocess.call(command, stdout=devnull, stderr=devnull)


def clamp(value, low, high):
    return max(low, min(high, value))


def clear_graph_leds():
    num_leds = int(getattr(backlight, "NUM_LEDS", 6))
    for led in range(num_leds):
        backlight.graph_set_led_polarity(led, 0)
        backlight.graph_set_led_state(led, 0)


def flash_edge_leds(flash_seconds):
    num_leds = int(getattr(backlight, "NUM_LEDS", 6))
    first = 0
    last = max(0, num_leds - 1)

    clear_graph_leds()
    for led in (first, last):
        backlight.graph_set_led_polarity(led, 1)
        backlight.graph_set_led_state(led, 0)

    time.sleep(clamp(float(flash_seconds), 0.05, 2.0))
    clear_graph_leds()


def split_text_lines(text, line_count):
    line_count = clamp(int(line_count), 1, 3)
    normalized = sanitize_lcd_text(text)
    if not normalized:
        return [""] * line_count
    if len(normalized) <= 16:
        out = [normalized]
        while len(out) < line_count:
            out.append("")
        return out

    words = normalized.split(" ")
    lines = [[] for _ in range(line_count)]

    for word in words:
        placed = False
        for line_words in lines:
            probe = " ".join(line_words + [word]).strip()
            if len(probe) <= 16:
                line_words.append(word)
                placed = True
                break

        if not placed:
            break

    out = [" ".join(line_words).strip() for line_words in lines]
    if not out[0]:
        packed = []
        for index in range(line_count):
            start = index * 16
            packed.append(normalized[start:start + 16])
        return packed

    return out


def color_with_brightness(base_rgb, brightness):
    scaled = []
    for value in base_rgb:
        scaled.append(int(clamp(int(value), 0, 255) * brightness / 100.0))
    return scaled


def choose_base_rgb(settings, args):
    has_rgb_override = args.r is not None or args.g is not None or args.b is not None
    normalized = settings
    if normalize_settings is not None:
        normalized = normalize_settings(settings)

    if THEMES and isinstance(normalized, dict):
        theme_index = clamp(int(normalized.get("theme_index", 0)), 0, len(THEMES) - 1)
        base = list(THEMES[theme_index][1])
    else:
        base = [0, 96, 160]

    if has_rgb_override:
        if args.r is not None:
            base[0] = clamp(int(args.r), 0, 255)
        if args.g is not None:
            base[1] = clamp(int(args.g), 0, 255)
        if args.b is not None:
            base[2] = clamp(int(args.b), 0, 255)

    return base


def apply_notify_style(settings, args):
    normalized = settings
    if normalize_settings is not None:
        normalized = normalize_settings(settings)

    base_rgb = choose_base_rgb(normalized, args)
    brightness = args.brightness
    if brightness is None and isinstance(normalized, dict):
        brightness = int(normalized.get("brightness", 70))
    brightness = clamp(int(brightness if brightness is not None else 70), 0, 100)

    contrast = args.contrast
    if contrast is None and isinstance(normalized, dict):
        contrast = int(normalized.get("contrast", 45))
    contrast = clamp(int(contrast if contrast is not None else 45), 0, 63)

    rgb = color_with_brightness(base_rgb, brightness)
    backlight.rgb(rgb[0], rgb[1], rgb[2])
    lcd.set_contrast(contrast)


def parse_args():
    parser = argparse.ArgumentParser(description="Display a temporary Display-O-Tron notification")
    parser.add_argument("--line1", default="Reply ready", help="First LCD line")
    parser.add_argument("--line2", default="Waiting input", help="Second LCD line")
    parser.add_argument("--line3", default="", help="Third LCD line (if available)")
    parser.add_argument("--title", help="Alias for --line1")
    parser.add_argument("--text", help="Auto-split message across available LCD lines")
    parser.add_argument("--seconds", type=int, default=8, help="Display duration in seconds")
    parser.add_argument("--r", type=int, help="Backlight red channel (0-255)")
    parser.add_argument("--g", type=int, help="Backlight green channel (0-255)")
    parser.add_argument("--b", type=int, help="Backlight blue channel (0-255)")
    parser.add_argument("--brightness", type=int, help="Backlight brightness percent (0-100)")
    parser.add_argument("--contrast", type=int, help="LCD contrast (0-63)")
    return parser.parse_args()


def main():
    args = parse_args()
    duration = clamp(int(args.seconds), 1, 120)

    had_status = run_quiet(["sudo", "-n", "systemctl", "is-active", "--quiet", SERVICE_NAME]) == 0
    if had_status:
        run_quiet(["sudo", "-n", "systemctl", "stop", SERVICE_NAME])

    settings = {"status_service_enabled": True}
    try:
        if load_settings is not None:
            settings = load_settings()

        apply_notify_style(settings, args)

        line1 = sanitize_lcd_text(args.line1)
        line2 = sanitize_lcd_text(args.line2)
        line3 = sanitize_lcd_text(args.line3)
        if args.title:
            line1 = sanitize_lcd_text(args.title)

        rows = clamp(int(getattr(lcd, "ROWS", 2)), 1, 3)
        if args.text:
            lines = split_text_lines(args.text, rows)
        else:
            lines = [line1, line2, line3]

        lcd.clear()
        for row in range(rows):
            lcd.set_cursor_position(0, row)
            lcd.write(fit(lines[row] if row < len(lines) else ""))

        flash_edge_leds(0.2)
        time.sleep(duration)
        print("NOTIFY_OK")
    finally:
        try:
            backlight.set_graph(0)
        except Exception:
            pass

        if settings.get("status_service_enabled", True):
            run_quiet(["sudo", "-n", "systemctl", "start", SERVICE_NAME])
        elif had_status:
            run_quiet(["sudo", "-n", "systemctl", "stop", SERVICE_NAME])


if __name__ == "__main__":
    main()
