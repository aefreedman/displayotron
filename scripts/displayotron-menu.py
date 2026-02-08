#!/usr/bin/env python3
from __future__ import print_function

import signal
import subprocess
import time

import dothat.lcd as lcd
import dothat.touch as nav
import dothat.backlight as backlight

from displayotron_common import SETTINGS_PATH
from displayotron_common import THEMES
from displayotron_common import apply_display
from displayotron_common import clamp
from displayotron_common import load_settings
from displayotron_common import save_settings
from displayotron_common import theme_name

SERVICE_NAME = "displayotron-status"

ITEMS = ["Theme", "Bright", "Contrast", "StatusSvc", "SaveExit"]


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
    with open("/dev/null", "w") as devnull:
        return subprocess.call(command, stdout=devnull, stderr=devnull)


class MenuApp(object):
    def __init__(self):
        self.running = True
        self.index = 0
        self.needs_redraw = True
        self.status_was_active = False
        self.settings = load_settings()
        self.settings_path = SETTINGS_PATH

    def apply_display(self):
        apply_display(lcd, backlight, self.settings)

    def line_value(self):
        item = ITEMS[self.index]
        if item == "Theme":
            return "{}".format(theme_name(self.settings["theme_index"]))
        if item == "Bright":
            return "{}%".format(self.settings["brightness"])
        if item == "Contrast":
            return "{}".format(self.settings["contrast"])
        if item == "StatusSvc":
            return "{}".format("on" if self.settings["status_service_enabled"] else "off")
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
            self.settings["theme_index"] = (self.settings["theme_index"] + delta) % len(THEMES)
        elif item == "Bright":
            self.settings["brightness"] = clamp(self.settings["brightness"] + (delta * 10), 0, 100)
        elif item == "Contrast":
            self.settings["contrast"] = clamp(self.settings["contrast"] + (delta * 2), 0, 63)
        elif item == "StatusSvc":
            if delta != 0:
                self.settings["status_service_enabled"] = not self.settings["status_service_enabled"]
        else:
            return

        self.apply_display()
        self.needs_redraw = True

    def select(self):
        if ITEMS[self.index] == "SaveExit":
            self.finish()

    def finish(self):
        save_settings(self.settings, self.settings_path)
        self.running = False

    def pause_status_service(self):
        if run_quiet(["sudo", "-n", "systemctl", "is-active", "--quiet", SERVICE_NAME]) == 0:
            self.status_was_active = True
            run_quiet(["sudo", "-n", "systemctl", "stop", SERVICE_NAME])

    def restore_status_service(self):
        if self.settings["status_service_enabled"]:
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
