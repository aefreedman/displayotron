#!/usr/bin/python3
from __future__ import print_function

import subprocess
import sys
import time

import dothat.backlight as backlight
import dothat.lcd as lcd

sys.path.insert(0, "/usr/local/bin")

try:
    from displayotron_common import apply_display
    from displayotron_common import load_settings
except Exception:
    apply_display = None
    load_settings = None


def run_quiet(command):
    with open("/dev/null", "w") as devnull:
        return subprocess.call(command, stdout=devnull, stderr=devnull)


def fit(text):
    cols = int(getattr(lcd, "COLS", 16))
    return str(text)[:cols].ljust(cols)


def clear_graph_leds():
    count = int(getattr(backlight, "NUM_LEDS", 6))
    for led in range(count):
        backlight.graph_set_led_polarity(led, 0)
        backlight.graph_set_led_state(led, 0)


def main():
    # Prevent status writer from overwriting the shutdown notice.
    run_quiet(["systemctl", "stop", "displayotron-status"])

    settings = {}
    try:
        if load_settings is not None:
            settings = load_settings()
    except Exception:
        settings = {}

    if apply_display is not None:
        try:
            apply_display(lcd, backlight, settings)
        except Exception:
            backlight.rgb(0, 120, 0)
    else:
        backlight.rgb(0, 120, 0)

    # Explicit safe/unplug state coloring.
    backlight.rgb(0, 120, 0)
    clear_graph_leds()

    rows = int(getattr(lcd, "ROWS", 2))
    lines = ["SAFE TO UNPLUG", "SYSTEM HALTED", "REMOVE POWER"]

    lcd.clear()
    for row in range(rows):
        text = ""
        if row < len(lines):
            text = lines[row]
        lcd.set_cursor_position(0, row)
        lcd.write(fit(text))

    # Small hold so users can see the transition before kernel shutdown continues.
    time.sleep(1.0)


if __name__ == "__main__":
    main()
