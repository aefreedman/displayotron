# Pi Display-O-Tron toolkit

This repo tracks local scripts and service files for a Raspberry Pi with a Pimoroni Display-O-Tron HAT.

## Layout

- `scripts/displayotron-check.sh` - hardware/software smoke checks, optional demo write
- `scripts/displayotron-status.py` - boot-time status display loop (IP + uptime)
- `scripts/displayotron-menu.py` - touch-driven settings menu for backlight/contrast/service mode
- `scripts/displayotron-notify.py` - temporary notification overlay on the LCD + side LEDs
- `scripts/displayotron-safe-unplug.py` - shutdown hook display message for safe unplug indication
- `scripts/displayotron_common.py` - shared settings/theme helpers used by scripts
- `scripts/deploy-to-pi.sh` - deploy tracked scripts and service files to a Pi
- `config/displayotron-settings.json` - tracked settings file deployed to Pi
- `systemd/displayotron-status.service` - systemd unit for the status display loop
- `systemd/displayotron-safe-unplug.service` - systemd unit that shows "SAFE TO UNPLUG" during shutdown
- `docs/displayotron-operations.md` - quick operations reference
- `migration-plan.md` - Stretch -> Bookworm migration plan

## Requirements

- SSH access to the Pi (`rpi` host alias in your SSH config)
- Passwordless sudo on Pi user (already configured)
- Display-O-Tron stack installed on Pi

## Deploy

From this repo root:

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

If your SSH alias is not `rpi`:

```bash
bash scripts/deploy-to-pi.sh --host pi@raspberrypi.local --enable --start
```

## Verify

```bash
ssh rpi "displayotron-check"
ssh rpi "systemctl status displayotron-status --no-pager"
ssh rpi "systemctl status displayotron-safe-unplug --no-pager"
ssh rpi "displayotron-check --leds"
ssh rpi "displayotron-notify --text 'Reply ready. Please check terminal.' --r 255 --g 0 --b 0 --brightness 50 --seconds 5"
```

## Safe unplug indicator

After deploy, shutdown automatically triggers a Display-O-Tron message:

- line 1: `SAFE TO UNPLUG`
- line 2: `SYSTEM HALTED`
- line 3: `REMOVE POWER`

This is wired via `displayotron-safe-unplug.service` and runs on `halt`/`poweroff` targets.
The shutdown indicator keeps side LEDs off.

## Settings source of truth

- Repo file: `config/displayotron-settings.json`
- Deployed file on Pi: `/home/pi/.config/displayotron/settings.json`

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
