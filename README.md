# Display-O-Tron toolkit

[![CI](https://github.com/aefreedman/displayotron/actions/workflows/ci.yml/badge.svg)](https://github.com/aefreedman/displayotron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/aefreedman/displayotron)](https://github.com/aefreedman/displayotron/releases)

This repo tracks local scripts and service files for a Raspberry Pi with a Pimoroni Display-O-Tron HAT.

## Layout

- `scripts/displayotron-check.sh` - hardware/software smoke checks, optional demo write
- `scripts/displayotron-status.py` - boot-time status display loop (IP + uptime)
- `scripts/displayotron-menu.py` - touch-driven settings menu for backlight/contrast/service mode
- `scripts/displayotron-notify.py` - temporary notification overlay on the LCD + side LEDs
- `scripts/displayotron-safe-unplug.py` - shutdown hook display message for safe unplug indication
- `scripts/displayotron_common.py` - shared settings/theme helpers used by scripts
- `scripts/deploy-to-pi.sh` - deploy tracked scripts and service files to a Raspberry Pi device
- `config/displayotron-settings.json` - tracked settings file deployed to the Raspberry Pi device
- `systemd/displayotron-status.service` - systemd unit for the status display loop
- `systemd/displayotron-safe-unplug.service` - systemd unit that shows "SAFE TO UNPLUG" during shutdown
- `docs/displayotron-operations.md` - quick operations reference

## Requirements

- SSH access to the Raspberry Pi device (`rpi` host alias in your SSH config)
- Passwordless sudo for the Raspberry Pi user (already configured)
- Display-O-Tron stack installed on the Raspberry Pi device

## Development

Install test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run local checks that do not require hardware:

```bash
python3 -m compileall -q scripts
bash -n scripts/displayotron-check.sh
bash -n scripts/deploy-to-pi.sh
python3 -m pytest -m "not pi" -q
```

## Deploy

From this repo root:

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

If your SSH alias is not `rpi`, pass an explicit SSH target:

```bash
bash scripts/deploy-to-pi.sh --host user@your-pi-host --enable --start
```

## Verify

```bash
ssh rpi "displayotron-check"
ssh rpi "systemctl status displayotron-status --no-pager"
ssh rpi "systemctl status displayotron-safe-unplug --no-pager"
ssh rpi "displayotron-check --leds"
ssh rpi "displayotron-notify --text 'Reply ready. Please check terminal.' --r 255 --g 0 --b 0 --brightness 50 --seconds 5"
```

## Status pages and touch controls

`displayotron-status` now has two pages:

- Page 1: large 3-line `HH:MM` digital clock
- Page 2: IP + uptime

Touch controls while status is running:

- `LEFT/RIGHT`: switch pages
- `UP/DOWN`: brightness down/up in 10% steps
- `CANCEL` (back): open `displayotron-menu`

Status and menu touch handlers apply debounce to reduce accidental double inputs.
Clock colon blink can be toggled in `displayotron-menu` via `ClockBlink`.

## Safe unplug indicator

After deploy, shutdown automatically triggers a Display-O-Tron message:

- line 1: `SAFE TO UNPLUG`
- line 2: `SYSTEM HALTED`
- line 3: `REMOVE POWER`

This is wired via `displayotron-safe-unplug.service` and runs on `halt`/`poweroff` targets.
The shutdown indicator keeps side LEDs off.

## Settings source of truth

- Repo file: `config/displayotron-settings.json`
- Deployed file on the Raspberry Pi device: `/home/pi/.config/displayotron/settings.json`

`displayotron-menu` and `displayotron-status` both read the same deployed settings file.
Editing `config/displayotron-settings.json` in this repo and redeploying will update live behavior.

## Touch settings menu

```bash
ssh rpi "displayotron-menu"
```

Controls:

- `UP/DOWN` navigate menu items
- `LEFT/RIGHT` change selected value
- `BUTTON` activate `SaveExit`
- `CANCEL` save and exit immediately
