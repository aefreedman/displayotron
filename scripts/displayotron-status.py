#!/usr/bin/env python3
from __future__ import print_function

import datetime
import os
import signal
import socket
import subprocess
import time

import dothat.backlight as backlight
import dothat.lcd as lcd
import dothat.touch as nav

from displayotron_common import apply_display
from displayotron_common import clamp
from displayotron_common import load_settings
from displayotron_common import save_settings


STATUS_PAGES = 2


def fit(text):
    cols = int(getattr(lcd, "COLS", 16))
    return str(text)[:cols].ljust(cols)


def is_press(event):
    if isinstance(event, bool):
        return event
    if isinstance(event, int):
        return event == 1
    token = str(event).lower().strip()
    return token in ("1", "press", "pressed", "down", "true")


class StatusApp(object):
    def __init__(self):
        self.running = True
        self.menu_open = False
        self.page_index = 0
        self.needs_redraw = True
        self.debounce_seconds = 0.2
        self.last_input_at = {}
        self.settings = load_settings()

        self.ip_text = "no network"
        self.uptime_text = "0m"
        self.last_ip_refresh = 0.0
        self.last_uptime_refresh = 0.0
        self.last_clock_second = None

    def apply_display(self):
        apply_display(lcd, backlight, self.settings)

    def refresh_settings(self):
        self.settings = load_settings()
        self.apply_display()

    def get_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "no network"
        finally:
            sock.close()

    def get_uptime_short(self):
        with open("/proc/uptime", "r", encoding="ascii") as uptime_file:
            total_seconds = int(float(uptime_file.read().split()[0]))
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            return "{}d{}h".format(days, hours)
        if hours > 0:
            return "{}h{}m".format(hours, minutes)
        return "{}m".format(minutes)

    def set_page(self, delta):
        if self.menu_open:
            return
        self.page_index = (self.page_index + delta) % STATUS_PAGES
        self.needs_redraw = True

    def adjust_brightness(self, delta):
        if self.menu_open:
            return

        new_value = clamp(self.settings.get("brightness", 70) + (delta * 10), 0, 100)
        if new_value == self.settings.get("brightness"):
            return

        self.settings["brightness"] = new_value
        save_settings(self.settings)
        self.apply_display()
        self.needs_redraw = True

    def open_menu(self):
        if self.menu_open:
            return

        self.menu_open = True
        lcd.clear()
        lcd.set_cursor_position(0, 0)
        lcd.write(fit("Opening menu..."))

        env = dict(os.environ)
        env["DISPLAYOTRON_MENU_EMBEDDED"] = "1"

        try:
            subprocess.call(["/usr/bin/python3", "/usr/local/bin/displayotron-menu"], env=env)
        finally:
            self.menu_open = False
            self.refresh_settings()
            self.needs_redraw = True

    def allow_input(self, key, event):
        if not is_press(event):
            return False
        if self.menu_open:
            return False

        now = time.time()
        previous = self.last_input_at.get(key, 0.0)
        if now - previous < self.debounce_seconds:
            return False

        self.last_input_at[key] = now
        return True

    def clock_lines(self):
        now = datetime.datetime.now()
        return [
            now.strftime("%H:%M:%S"),
            now.strftime("%a %b %d"),
            now.strftime("%Y"),
        ]

    def system_lines(self):
        return [
            "IP {}".format(self.ip_text),
            "Up {}".format(self.uptime_text),
            "Bri {}%  ^/v".format(self.settings.get("brightness", 70)),
        ]

    def draw(self):
        if self.menu_open:
            return

        lines = self.clock_lines() if self.page_index == 0 else self.system_lines()
        rows = int(getattr(lcd, "ROWS", 2))
        lcd.clear()
        for row in range(rows):
            text = ""
            if row < len(lines):
                text = lines[row]
            lcd.set_cursor_position(0, row)
            lcd.write(fit(text))

        self.needs_redraw = False

    def periodic_refresh(self):
        now = time.time()

        current_second = int(now)
        if self.page_index == 0 and current_second != self.last_clock_second:
            self.last_clock_second = current_second
            self.needs_redraw = True

        if now - self.last_ip_refresh >= 15.0:
            self.ip_text = self.get_ip()
            self.last_ip_refresh = now
            if self.page_index == 1:
                self.needs_redraw = True

        if now - self.last_uptime_refresh >= 10.0:
            self.uptime_text = self.get_uptime_short()
            self.last_uptime_refresh = now
            if self.page_index == 1:
                self.needs_redraw = True


APP = StatusApp()


def on_signal(signum, frame):
    del signum, frame
    APP.running = False


@nav.on(nav.LEFT)
def on_left(channel, event):
    del channel
    if APP.allow_input("left", event):
        APP.set_page(-1)


@nav.on(nav.RIGHT)
def on_right(channel, event):
    del channel
    if APP.allow_input("right", event):
        APP.set_page(1)


@nav.on(nav.UP)
def on_up(channel, event):
    del channel
    if APP.allow_input("up", event):
        APP.adjust_brightness(1)


@nav.on(nav.DOWN)
def on_down(channel, event):
    del channel
    if APP.allow_input("down", event):
        APP.adjust_brightness(-1)


@nav.on(nav.CANCEL)
def on_cancel(channel, event):
    del channel
    if APP.allow_input("cancel", event):
        APP.open_menu()


def main():
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    APP.apply_display()
    APP.periodic_refresh()
    APP.draw()

    while APP.running:
        APP.periodic_refresh()
        if APP.needs_redraw:
            APP.draw()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
