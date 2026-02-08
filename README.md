# Pi Display-O-Tron toolkit

This repo tracks local scripts and service files for a Raspberry Pi with a Pimoroni Display-O-Tron HAT.

## Layout

- `scripts/displayotron-check.sh` - hardware/software smoke checks, optional demo write
- `scripts/displayotron-status.py` - boot-time status display loop (IP + uptime)
- `scripts/displayotron-menu.py` - touch-driven settings menu for backlight/contrast/service mode
- `scripts/deploy-to-pi.sh` - deploy tracked scripts and service files to a Pi
- `systemd/displayotron-status.service` - systemd unit for the status display loop
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
```

## Touch settings menu

```bash
ssh rpi "displayotron-menu"
```

Controls:

- `UP/DOWN` navigate menu items
- `LEFT/RIGHT` change selected value
- `BUTTON` activate `SaveExit`
- `CANCEL` save and exit immediately
