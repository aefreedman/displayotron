# AGENTS.md

Guidance for coding agents working in this repository.

## Repository overview

- Project: Raspberry Pi Display-O-Tron toolkit.
- Languages: Python 3 and Bash.
- Target: Raspberry Pi OS with Pimoroni Display-O-Tron libs (`dothat`, `sn3218`).
- Deployment: copy scripts/services to the Raspberry Pi device and control them with systemd.
- No package build system (`pyproject.toml`, `setup.py`, `Makefile` are absent).
- Test framework: `pytest` configured via `pytest.ini`.

## Source layout

- `scripts/displayotron-status.py` / `scripts/displayotron-menu.py` - primary runtime UIs.
- `scripts/displayotron-notify.py` / `scripts/displayotron-safe-unplug.py` - temporary + shutdown displays.
- `scripts/displayotron_common.py` - shared settings/theme helpers.
- `scripts/displayotron-check.sh`, `scripts/deploy-to-pi.sh`, `systemd/*.service`, `config/displayotron-settings.json` - operations/deploy assets.
- `tests/unit/test_displayotron_common.py` - unit coverage for settings/theme helper behavior.
- `tests/conftest.py` - test import path setup for `scripts/` modules.

## Environment assumptions

- Agents commonly run off-device, without Display-O-Tron hardware.
- Functional validation usually requires remote execution on the Raspberry Pi device over SSH.
- Default SSH alias is `rpi` unless `--host` is passed.
- Scripts use non-interactive sudo on the Raspberry Pi device (`sudo -n` style).

## Build, lint, and test commands

There is no compile/build pipeline; use syntax checks + smoke tests.

Install dev dependencies first:

```bash
python3 -m pip install -r requirements-dev.txt
```

### Local static checks (safe off-device)

```bash
python3 -m compileall -q scripts
bash -n scripts/displayotron-check.sh
bash -n scripts/deploy-to-pi.sh
python3 -m pytest -q
python3 -m pytest -m "not pi" -q
```

### Deploy to Raspberry Pi

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

With explicit host:

```bash
bash scripts/deploy-to-pi.sh --host user@your-pi-host --enable --start
```

### Smoke tests on the Raspberry Pi device

```bash
ssh rpi "displayotron-check"
ssh rpi "displayotron-check --demo"
ssh rpi "displayotron-check --leds"
```

Service and logs:

```bash
ssh rpi "sudo systemctl status displayotron-status --no-pager"
ssh rpi "sudo systemctl status displayotron-safe-unplug --no-pager"
ssh rpi "journalctl -u displayotron-status -n 100 --no-pager"
ssh rpi "displayotron-notify --text 'Reply ready. Please check terminal.' --seconds 5"
```

### Running a single test (important)

Primary single-test command (local unit test):

```bash
python3 -m pytest tests/unit/test_displayotron_common.py::test_normalize_settings_clamps_and_coerces -q
```

Alternative single-test command (single test file):

```bash
python3 -m pytest tests/unit/test_displayotron_common.py -q
```

Hardware single-test equivalents on the Raspberry Pi device:

```bash
ssh rpi "displayotron-check --demo"
```

Other Raspberry Pi device single-test equivalents:

```bash
ssh rpi "displayotron-check --leds"
ssh rpi "sudo systemctl restart displayotron-status && sudo systemctl status displayotron-status --no-pager"
```

Pytest marker notes:

- Use `-m "not pi"` for local/off-device runs.
- Use `-m pi` only for tests that explicitly require Raspberry Pi hardware/services.

## Code style and conventions

### Python script structure

- Use Python 3.
- Keep a shebang at the top (prefer existing file style).
- Preserve `main()` and `if __name__ == "__main__": main()` entry pattern.

### Imports

- Group imports with blank lines:
  1) standard library
  2) third-party (`dothat.*`)
  3) local modules (`displayotron_common`)
- Prefer one import per line.
- Match surrounding style within each file.

### Formatting

- Follow existing PEP 8-like style (4 spaces, no tabs).
- Keep functions focused and readable.
- Reuse helpers (`fit`, `clamp`, `run_quiet`) instead of duplicating logic.

### Types and data handling

- Codebase is mostly untyped; do not add typing-only dependencies.
- Validate and clamp user/config values (`brightness`, `contrast`, indices).
- Normalize settings via shared helpers before hardware writes.
- Keep JSON settings backward-compatible and robust to malformed input.

### Naming

- `snake_case` for functions/variables.
- `UPPER_CASE` for constants.
- `PascalCase` for classes.
- Prefer descriptive hardware/action names (`clear_graph_leds`, `apply_display`).

### Error handling

- Fail soft when optional hardware/service calls fail.
- Use guarded fallbacks for import/hardware availability issues.
- Keep subprocess noise low with `run_quiet` where appropriate.
- Avoid bare `except:`; use explicit exceptions or `except Exception:`.

### LCD/LED behavior rules

- Always fit text to display width (`lcd.COLS`) before writing.
- Sanitize LCD text to safe ASCII when needed.
- Clear graph LEDs after temporary animations.
- Respect current theme/brightness/contrast unless an explicit override is requested.

### Shell + systemd conventions

- Keep `set -euo pipefail` in shell scripts.
- Quote shell variables and paths.
- Use `case`-based CLI parsing for script options.
- Keep scripts non-interactive and automation-friendly.
- Keep systemd units explicit and minimal (`Type`, `ExecStart`, restart policy/order).
- Preserve safe-unplug shutdown ordering behavior.

## Agent workflow

1. Read related scripts and shared helpers first.
2. Make minimal, focused edits.
3. Run local syntax + unit tests (`compileall`, `bash -n`, `pytest`).
4. For behavior changes, run remote Raspberry Pi device smoke checks.
5. Update docs when flags/settings/service behavior change.

## Cursor/Copilot rules status

Checked locations:

- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

Result: no Cursor or Copilot rule files were found in this repository.
If these files are added later, treat them as authoritative and merge them into this guide.
