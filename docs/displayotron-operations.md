# Display-O-Tron operations

## Deploy tracked scripts to the Raspberry Pi device

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

With an explicit SSH target:

```bash
bash scripts/deploy-to-pi.sh --host user@your-pi-host --enable --start
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

## Status pages and touch controls

While `displayotron-status` is running:

- Page 1: large 3-line `HH:MM` digital clock
- Page 2: IP + uptime

Controls:

- `LEFT/RIGHT`: switch status pages
- `UP/DOWN`: adjust backlight brightness (10% steps)
- `CANCEL` (back): open settings menu

Touch input is debounced in both status and menu views to reduce accidental double presses.

Menu controls:

- `UP/DOWN`: select menu item
- `LEFT/RIGHT`: change selected value
- `BUTTON`: activate `SaveExit`
- `CANCEL`: save and exit

Settings currently available:

- Theme preset (`Blue`, `Green`, `Amber`, `White`, `Purple`, `Off`)
- Backlight brightness (`0-100%`, 10% steps)
- LCD contrast (`0-63`, 2-step increments)
- `ClockBlink` toggle (blink/steady colon in status clock view)
- `StatusSvc` toggle (start/stop `displayotron-status` when menu exits)

## Known hardware limitation: no true text rotation

The Display-O-Tron character LCD stack (`dothat` -> `st7036`) does not expose a 180-degree
glyph rotation mode. We can remap touch direction, but cannot make letters render upright when
the display is physically upside down.

Evidence collected on-device:

- Available `st7036.st7036` methods include cursor/shift/contrast APIs, but no rotate/invert API.
- `set_display_mode(enable, cursor, blink)` only toggles display/cursor/blink.
- `set_cursor_position(column, row)` writes DDRAM offsets only.
- `write(value)` sends raw character bytes via SPI (`self.spi.xfer([i])`).

Repro commands:

```bash
ssh rpi "python3 - <<'PY'
import inspect, st7036
print([n for n in dir(st7036.st7036) if not n.startswith('_')])
print(inspect.getsource(st7036.st7036.set_display_mode))
print(inspect.getsource(st7036.st7036.set_cursor_position))
print(inspect.getsource(st7036.st7036.write))
PY"
```

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
ssh rpi "sudo systemctl status displayotron-safe-unplug --no-pager"
```

## Safe unplug workflow

Use normal shutdown:

```bash
ssh rpi "sudo shutdown -h now"
```

During halt, the shutdown hook sets the display to:

- `SAFE TO UNPLUG`
- `SYSTEM HALTED`
- `REMOVE POWER`

The shutdown indicator intentionally keeps graph/side LEDs off.

If you want to test the indicator without shutting down:

```bash
ssh rpi "sudo systemctl start displayotron-safe-unplug"
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
