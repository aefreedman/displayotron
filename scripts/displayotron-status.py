#!/usr/bin/env python3
import socket
import time

import dothat.backlight as backlight
import dothat.lcd as lcd

from displayotron_common import apply_display
from displayotron_common import load_settings


def fit(text):
    return str(text)[:16].ljust(16)


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "no network"
    finally:
        sock.close()


def get_uptime_short():
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


def draw():
    lcd.clear()
    lcd.set_cursor_position(0, 0)
    lcd.write(fit("IP {}".format(get_ip())))
    lcd.set_cursor_position(0, 1)
    lcd.write(fit("Up {}".format(get_uptime_short())))


def main():
    while True:
        settings = load_settings()
        apply_display(lcd, backlight, settings)
        draw()
        time.sleep(5)


if __name__ == "__main__":
    main()
