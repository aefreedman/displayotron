#!/usr/bin/env python3
from __future__ import print_function

import json
import os
import signal
import subprocess
import time

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav


SETTINGS_PATH = os.path.expanduser("~/.config/displayotron/menu-settings.json")
SERVICE_NAME = "displayotron-status"

THEMES = [
    ("Blue", (0, 96, 160)),
    ("Green", (0, 140, 40)),
    ("Amber", (160, 90, 0)),
    ("White", (180, 180, 180)),
    ("Purple", (120, 40, 160)),
    ("Off", (0, 0, 0)),
]

ITEMS = ["Theme", "Bright", "Contrast", "StatusSvc", "SaveExit"]


def clamp(value, low, high):
    return max(low, min(high, value))


def fit(text):
    return str(text)[:16].ljust(16)


def is_press(event):
    if isinstance(event, bool):
        return event
    if isinstance(event, int):
        return event == 1
    token = str(event).lower().strip()
    return token in ("1", "press", "pressed", "down", "true")


def run_quiet(command):
    with open(os.devnull, "w") as devnull:
        return subprocess.call(command, stdout=devnull, stderr=devnull)


class MenuApp(object):
    def __init__(self):
        self.running = True
        self.index = 0
        self.needs_redraw = True
        self.status_was_active = False

        self.theme_index = 0
        self.brightness = 70
        self.contrast = 45
        self.status_service_enabled = True

        self.load_settings()

    def load_settings(self):
        try:
            with open(SETTINGS_PATH, "r") as settings_file:
                data = json.load(settings_file)
        except (IOError, ValueError):
            return

        self.theme_index = clamp(int(data.get("theme_index", self.theme_index)), 0, len(THEMES) - 1)
        self.brightness = clamp(int(data.get("brightness", self.brightness)), 0, 100)
        self.contrast = clamp(int(data.get("contrast", self.contrast)), 0, 63)
        self.status_service_enabled = bool(data.get("status_service_enabled", self.status_service_enabled))

    def save_settings(self):
        directory = os.path.dirname(SETTINGS_PATH)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        data = {
            "theme_index": self.theme_index,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "status_service_enabled": self.status_service_enabled,
        }

        with open(SETTINGS_PATH, "w") as settings_file:
            json.dump(data, settings_file, indent=2, sort_keys=True)

    def apply_display(self):
        base = THEMES[self.theme_index][1]
        scaled = []
        for value in base:
            scaled.append(int(value * self.brightness / 100.0))
        backlight.rgb(scaled[0], scaled[1], scaled[2])
        lcd.set_contrast(self.contrast)

    def line_value(self):
        item = ITEMS[self.index]
        if item == "Theme":
            return "{}".format(THEMES[self.theme_index][0])
        if item == "Bright":
            return "{}%".format(self.brightness)
        if item == "Contrast":
            return "{}".format(self.contrast)
        if item == "StatusSvc":
            return "{}".format("on" if self.status_service_enabled else "off")
        return "B=save C=quit"

    def draw(self):
        title = ">{}/{} {}".format(self.index + 1, len(ITEMS), ITEMS[self.index])
        lcd.clear()
        lcd.set_cursor_position(0, 0)
        lcd.write(fit(title))
        lcd.set_cursor_position(0, 1)
        lcd.write(fit(self.line_value()))
        self.needs_redraw = False

    def move(self, delta):
        self.index = (self.index + delta) % len(ITEMS)
        self.needs_redraw = True

    def adjust(self, delta):
        item = ITEMS[self.index]
        if item == "Theme":
            self.theme_index = (self.theme_index + delta) % len(THEMES)
        elif item == "Bright":
            self.brightness = clamp(self.brightness + (delta * 10), 0, 100)
        elif item == "Contrast":
            self.contrast = clamp(self.contrast + (delta * 2), 0, 63)
        elif item == "StatusSvc":
            if delta != 0:
                self.status_service_enabled = not self.status_service_enabled
        else:
            return

        self.apply_display()
        self.needs_redraw = True

    def select(self):
        if ITEMS[self.index] == "SaveExit":
            self.finish()

    def finish(self):
        self.save_settings()
        self.running = False

    def pause_status_service(self):
        if run_quiet(["sudo", "-n", "systemctl", "is-active", "--quiet", SERVICE_NAME]) == 0:
            self.status_was_active = True
            run_quiet(["sudo", "-n", "systemctl", "stop", SERVICE_NAME])

    def restore_status_service(self):
        if self.status_service_enabled:
            run_quiet(["sudo", "-n", "systemctl", "start", SERVICE_NAME])
        elif self.status_was_active:
            run_quiet(["sudo", "-n", "systemctl", "stop", SERVICE_NAME])


APP = MenuApp()


def on_signal(signum, frame):
    del signum, frame
    APP.finish()


@nav.on(nav.UP)
def on_up(channel, event):
    del channel
    if is_press(event):
        APP.move(-1)


@nav.on(nav.DOWN)
def on_down(channel, event):
    del channel
    if is_press(event):
        APP.move(1)


@nav.on(nav.LEFT)
def on_left(channel, event):
    del channel
    if is_press(event):
        APP.adjust(-1)


@nav.on(nav.RIGHT)
def on_right(channel, event):
    del channel
    if is_press(event):
        APP.adjust(1)


@nav.on(nav.BUTTON)
def on_button(channel, event):
    del channel
    if is_press(event):
        APP.select()


@nav.on(nav.CANCEL)
def on_cancel(channel, event):
    del channel
    if is_press(event):
        APP.finish()


def main():
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    APP.pause_status_service()
    APP.apply_display()

    try:
        while APP.running:
            if APP.needs_redraw:
                APP.draw()
            time.sleep(0.05)
    finally:
        APP.restore_status_service()


if __name__ == "__main__":
    main()
