#!/usr/bin/env bash
set -euo pipefail

HOST="rpi"
ENABLE=0
START=0

usage() {
  cat <<'EOF'
Usage: deploy-to-pi.sh [options]

Options:
  --host <ssh-target>   SSH target/alias (default: rpi)
  --enable              Enable displayotron-status service
  --start               Start/restart displayotron-status service
  -h, --help            Show this help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --enable)
      ENABLE=1
      shift
      ;;
    --start)
      START=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [ -z "$HOST" ]; then
  echo "Missing host value" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

CHECK_SCRIPT="$ROOT_DIR/scripts/displayotron-check.sh"
STATUS_SCRIPT="$ROOT_DIR/scripts/displayotron-status.py"
MENU_SCRIPT="$ROOT_DIR/scripts/displayotron-menu.py"
COMMON_PY="$ROOT_DIR/scripts/displayotron_common.py"
SETTINGS_FILE="$ROOT_DIR/config/displayotron-settings.json"
SERVICE_FILE="$ROOT_DIR/systemd/displayotron-status.service"

for path in "$CHECK_SCRIPT" "$STATUS_SCRIPT" "$MENU_SCRIPT" "$COMMON_PY" "$SETTINGS_FILE" "$SERVICE_FILE"; do
  if [ ! -f "$path" ]; then
    echo "Missing file: $path" >&2
    exit 1
  fi
done

echo "Deploying files to $HOST"
scp "$CHECK_SCRIPT" "$HOST:/tmp/displayotron-check.sh"
scp "$STATUS_SCRIPT" "$HOST:/tmp/displayotron-status.py"
scp "$MENU_SCRIPT" "$HOST:/tmp/displayotron-menu.py"
scp "$COMMON_PY" "$HOST:/tmp/displayotron_common.py"
scp "$SETTINGS_FILE" "$HOST:/tmp/displayotron-settings.json"
scp "$SERVICE_FILE" "$HOST:/tmp/displayotron-status.service"

ssh "$HOST" "sudo install -m 755 /tmp/displayotron-check.sh /usr/local/bin/displayotron-check && sudo install -m 755 /tmp/displayotron-status.py /usr/local/bin/displayotron-status && sudo install -m 755 /tmp/displayotron-menu.py /usr/local/bin/displayotron-menu && sudo install -m 644 /tmp/displayotron_common.py /usr/local/bin/displayotron_common.py && sudo install -d -m 755 -o pi -g pi /home/pi/.config/displayotron && sudo install -m 644 -o pi -g pi /tmp/displayotron-settings.json /home/pi/.config/displayotron/settings.json && sudo install -m 644 /tmp/displayotron-status.service /etc/systemd/system/displayotron-status.service && rm -f /tmp/displayotron-check.sh /tmp/displayotron-status.py /tmp/displayotron-menu.py /tmp/displayotron_common.py /tmp/displayotron-settings.json /tmp/displayotron-status.service && sudo systemctl daemon-reload"

if [ "$ENABLE" -eq 1 ]; then
  echo "Enabling displayotron-status service"
  ssh "$HOST" "sudo systemctl enable displayotron-status"
fi

if [ "$START" -eq 1 ]; then
  echo "Starting displayotron-status service"
  ssh "$HOST" "sudo systemctl restart displayotron-status"
fi

echo "Running remote health check"
ssh "$HOST" "displayotron-check"

echo "Deploy complete"
