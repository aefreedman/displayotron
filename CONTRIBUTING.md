# Contributing

Thanks for your interest in improving Display-O-Tron.

## Scope

This repository contains scripts, services, and configuration for running a Pimoroni Display-O-Tron on a Raspberry Pi device.

Because most contributors will work off-device, please keep changes friendly to both environments:

- local/off-device development without hardware
- on-device validation on a Raspberry Pi with the Display-O-Tron stack installed

## Development setup

Install test dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

## Local checks

Run these before opening a pull request:

```bash
python3 -m compileall -q scripts
bash -n scripts/displayotron-check.sh
bash -n scripts/deploy-to-pi.sh
python3 -m pytest -m "not pi" -q
```

## Hardware validation

If your change affects runtime behavior, also validate on the Raspberry Pi device when possible:

```bash
ssh rpi "displayotron-check"
ssh rpi "displayotron-check --demo"
ssh rpi "displayotron-check --leds"
ssh rpi "sudo systemctl status displayotron-status --no-pager"
```

## Style guidelines

- use Python 3
- keep changes focused and minimal
- preserve existing script entry points
- reuse shared helpers in `scripts/displayotron_common.py`
- validate and clamp user/config values
- keep shell scripts non-interactive and automation-friendly
- avoid introducing hardware-only assumptions into off-device code paths

## Tests

- off-device tests should live under `tests/`
- hardware-dependent tests should be clearly marked with `@pytest.mark.pi`
- keep test coverage focused on shared logic when hardware is unavailable

## Pull requests

Please include:

- a short summary of the change
- why the change is needed
- test results
- any Raspberry Pi / hardware validation notes, if applicable

## Documentation

Update docs when you change:

- flags or CLI behavior
- settings shape or defaults
- deployment steps
- systemd service behavior
