# Raspberry Pi 3 Migration Plan (Stretch -> Bookworm)

## Goal
Migrate from end-of-life Stretch to Raspberry Pi OS Bookworm with a low-risk rollback path.

## Current state
- Device reachable over SSH (`rpi` alias)
- Legacy apt mirror quick-fix applied for temporary maintenance
- System is still on Stretch and should be replaced, not upgraded in place

## Recommended approach
Use a fresh SD card image (Bookworm) and restore only required data/config.

## 1) Backup and inventory old system
- Save package list: `dpkg --get-selections > ~/pkg-selections.txt`
- Save enabled services: `systemctl list-unit-files --state=enabled > ~/enabled-services.txt`
- Backup key configs:
  - `/etc/fstab`
  - `/etc/hostname`
  - `/etc/hosts`
  - `/etc/dhcpcd.conf`
  - `/etc/wpa_supplicant/wpa_supplicant.conf` (if Wi-Fi)
- Backup user/app data (prefer `rsync`) to another machine
- Optional: full SD image backup for hard rollback

## 2) Prepare new Bookworm SD card
- Use Raspberry Pi Imager
- Choose Raspberry Pi OS Lite (Bookworm, 32-bit)
- Preconfigure:
  - hostname
  - username/password (prefer non-default user)
  - SSH enabled with key auth
  - locale/timezone/Wi-Fi (if needed)

## 3) First boot checks
- Verify SSH login
- Run updates:
  - `sudo apt update`
  - `sudo apt full-upgrade -y`
  - `sudo reboot`

## 4) Restore selectively
- Reinstall required packages from inventory
- Restore app configs carefully (avoid blanket overwrite of `/etc`)
- Restore service data and validate each workload

## 5) Hardening
- Prefer SSH key-only auth
- Disable password SSH once confirmed
- Enable unattended upgrades
- Add simple monitoring checks (disk/temp/failed services)

## Cutover and rollback
- Cutover: switch to new SD after validation
- Rollback: reinsert old SD if needed
- Keep old SD untouched for 1-2 weeks

## Note
The Stretch mirror quick-fix is temporary. Long-term stable path is fresh Bookworm install.
