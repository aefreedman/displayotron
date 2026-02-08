# Display-O-Tron operations

## Deploy tracked scripts to Pi

```bash
bash scripts/deploy-to-pi.sh --enable --start
```

## Check health

```bash
ssh rpi "displayotron-check"
ssh rpi "displayotron-check --demo"
```

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
