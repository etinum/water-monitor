#!/bin/bash
# Install the water monitor server on the Mac mini (run ON the mini). No sudo needed.
# Usage: bash install_server.sh
set -euo pipefail

INSTALL_DIR="/Users/erictran/Script/water-monitor"
PLIST_NAME="com.erictran.water-monitor.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Water Monitor Server install ==="

# 1. Copy files into place (skip if running from the install dir already)
mkdir -p "$INSTALL_DIR"
if [ "$(pwd)" != "$INSTALL_DIR" ]; then
    cp water_server.py config.py requirements.txt status.sh run_server.sh "$PLIST_NAME" "$INSTALL_DIR/"
fi
chmod +x "$INSTALL_DIR/run_server.sh" "$INSTALL_DIR/status.sh"

# 2. Python environment (prefers uv-managed python if present)
if [ ! -d "$INSTALL_DIR/venv" ]; then
    if [ -x "$HOME/.local/bin/uv" ]; then
        "$HOME/.local/bin/uv" venv --python 3.12 "$INSTALL_DIR/venv"
    else
        python3 -m venv "$INSTALL_DIR/venv"
    fi
fi
if [ -x "$HOME/.local/bin/uv" ]; then
    "$HOME/.local/bin/uv" pip install --quiet --python "$INSTALL_DIR/venv/bin/python3" -r "$INSTALL_DIR/requirements.txt"
else
    "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
fi
echo "✓ Python environment ready"

# 3. Install as a LaunchAgent (starts tmux session at login, re-checks every 5 min)
launchctl bootout "gui/$(id -u)/com.erictran.water-monitor" 2>/dev/null || true
cp "$INSTALL_DIR/$PLIST_NAME" "$PLIST_DEST"
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"
echo "✓ LaunchAgent installed and started"

sleep 3
echo ""
echo "=== Status ==="
/opt/homebrew/bin/tmux ls 2>/dev/null | grep water-monitor && echo "✓ tmux session running" || echo "⚠ tmux session not found"
echo ""
echo "Watch live:  tmux attach -t water-monitor   (detach: ctrl-b d)"
echo "Logs:        tail -f $INSTALL_DIR/water_monitor.log"
