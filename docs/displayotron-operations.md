# Display-O-Tron operations

## Deploy tracked scripts to Pi

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

This deploy also copies `config/displayotron-settings.json` to:

- `/home/pi/.config/displayotron/settings.json`

## Check health

```bash
ssh rpi "displayotron-check"
ssh rpi "displayotron-check --demo"
ssh rpi "displayotron-check --leds"
ssh rpi "displayotron-notify --text 'Reply ready. Please check terminal.' --r 255 --g 0 --b 0 --brightness 50 --seconds 5"
```

## Show temporary notification

```bash
ssh rpi "displayotron-notify --text 'Input required. Please check terminal.' --r 255 --g 0 --b 0 --brightness 50 --seconds 8"
```

You can also provide explicit line content:

```bash
ssh rpi "displayotron-notify --line1 'Reply ready' --line2 'Please check' --line3 'terminal' --seconds 8"
```

## Touch settings menu

```bash
ssh rpi "displayotron-menu"
```

Menu controls:

- `UP/DOWN`: select menu item
- `LEFT/RIGHT`: change selected value
- `BUTTON`: activate `SaveExit`
- `CANCEL`: save and exit

Settings currently available:

- Theme preset (`Blue`, `Green`, `Amber`, `White`, `Purple`, `Off`)
- Backlight brightness (`0-100%`, 10% steps)
- LCD contrast (`0-63`, 2-step increments)
- `StatusSvc` toggle (start/stop `displayotron-status` when menu exits)

## Edit settings from git repo

1. Edit `config/displayotron-settings.json`
2. Redeploy:

```bash
bash scripts/deploy-to-pi.sh --start
```

`displayotron-status` will then use the updated theme/brightness/contrast values.

## Service control

```bash
ssh rpi "sudo systemctl status displayotron-status --no-pager"
ssh rpi "sudo systemctl restart displayotron-status"
ssh rpi "sudo systemctl disable --now displayotron-status"
```

## Logs

```bash
ssh rpi "journalctl -u displayotron-status -n 100 --no-pager"
```

## Backlight control surface (Python)

From `dothat.backlight`:

- `rgb(r, g, b)` full backlight color
- `left_rgb(...)`, `mid_rgb(...)`, `right_rgb(...)` segmented color control
- `off()` turn backlight off
- `set_graph(...)` and `set_bar(...)` graph LEDs
