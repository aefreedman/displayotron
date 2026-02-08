#!/usr/bin/env bash
set -euo pipefail

DEMO=0
if [ "${1:-}" = "--demo" ]; then
  DEMO=1
elif [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  echo "Usage: displayotron-check [--demo]"
  echo "  --demo  Write test text + backlight color after checks"
  exit 0
fi

STATUS=0

ok() { printf '[OK]   %s\n' "$1"; }
warn() { printf '[WARN] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; STATUS=1; }

if [ -e /dev/i2c-1 ]; then
  ok "/dev/i2c-1 present"
else
  fail "/dev/i2c-1 missing (I2C not enabled)"
fi

if [ -e /dev/spidev0.0 ] && [ -e /dev/spidev0.1 ]; then
  ok "SPI device nodes present"
else
  fail "SPI device nodes missing (SPI not enabled)"
fi

I2CDETECT_BIN=""
if command -v i2cdetect >/dev/null 2>&1; then
  I2CDETECT_BIN="$(command -v i2cdetect)"
elif [ -x /usr/sbin/i2cdetect ]; then
  I2CDETECT_BIN="/usr/sbin/i2cdetect"
fi

if [ -n "$I2CDETECT_BIN" ]; then
  SCAN=""
  if SCAN=$(sudo -n "$I2CDETECT_BIN" -y 1 2>/dev/null); then
    :
  elif SCAN=$("$I2CDETECT_BIN" -y 1 2>/dev/null); then
    :
  else
    warn "i2cdetect failed"
  fi

  if [ -n "$SCAN" ]; then
    if [[ "$SCAN" == *"2c"* ]]; then
      ok "I2C bus sees device 0x2c (expected for DotHAT backlight)"
    else
      warn "I2C scan did not show 0x2c; check HAT seating"
    fi
  fi
else
  warn "i2c-tools not installed"
fi

PYOUT=$(python3 - <<'PY'
import importlib

mods = ["dothat.lcd", "dothat.backlight", "dothat.touch", "sn3218"]
failed = []

for module_name in mods:
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        failed.append((module_name, str(exc)))

if failed:
    for module_name, error_text in failed:
        print("IMPORT_FAIL", module_name, error_text)
    raise SystemExit(1)

print("IMPORT_OK")
PY
) || {
  fail "Python import check failed"
  printf '%s\n' "$PYOUT"
}

if [ "${PYOUT:-}" = "IMPORT_OK" ]; then
  ok "Python module imports succeeded"
fi

if [ "$DEMO" -eq 1 ]; then
  if python3 - <<'PY'
import sys

import dothat.lcd as lcd
import dothat.backlight as backlight

lcd.clear()
lcd.set_cursor_position(0, 0)
lcd.write("Display-O-Tron")
lcd.set_cursor_position(0, 1)
lcd.write("check: PASS    ")

sys.path.insert(0, "/usr/local/bin")
try:
    from displayotron_common import apply_display, load_settings

    apply_display(lcd, backlight, load_settings())
except Exception:
    backlight.rgb(0, 96, 160)

print("DEMO_OK")
PY
  then
    ok "Demo written to LCD and backlight set"
  else
    fail "Demo write failed"
  fi
fi

if [ "$STATUS" -eq 0 ]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL"
fi

exit "$STATUS"
