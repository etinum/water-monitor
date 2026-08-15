#!/bin/bash
# Install the water monitor server on the Mac mini (run ON the mini).
# Requires sudo: the server MUST run as a system LaunchDaemon, see TROUBLESHOOTING.md.
# Usage: sudo bash install_server.sh
set -euo pipefail

INSTALL_DIR="/Users/erictran/Script/water-monitor"
PLIST_NAME="com.erictran.water-monitor.plist"
PLIST_DEST="/Library/LaunchDaemons/$PLIST_NAME"
REAL_USER="${SUDO_USER:-erictran}"

if [ "$(id -u)" -ne 0 ]; then
    echo "This installer must run with sudo (system LaunchDaemon install)." >&2
    exit 1
fi

echo "=== Water Monitor Server install ==="

# 1. Copy files into place (skip if running from the install dir already)
mkdir -p "$INSTALL_DIR"
if [ "$(pwd)" != "$INSTALL_DIR" ]; then
    cp water_server.py config.py requirements.txt status.sh "$PLIST_NAME" "$INSTALL_DIR/"
    chown "$REAL_USER" "$INSTALL_DIR"/*.py "$INSTALL_DIR"/*.sh "$INSTALL_DIR/$PLIST_NAME"
fi
chmod +x "$INSTALL_DIR/status.sh"

# 2. Python environment (prefers uv-managed python if present), created as the real user.
# Only touched when deps are actually missing — running uv/pip under sudo is fragile
# (cache + HOME ownership) and must never block the launchd install below.
USER_HOME=$(eval echo "~$REAL_USER")
if [ ! -d "$INSTALL_DIR/venv" ]; then
    if [ -x "$USER_HOME/.local/bin/uv" ]; then
        sudo -u "$REAL_USER" "$USER_HOME/.local/bin/uv" venv --python 3.12 "$INSTALL_DIR/venv"
    else
        sudo -u "$REAL_USER" python3 -m venv "$INSTALL_DIR/venv"
    fi
fi
if sudo -u "$REAL_USER" "$INSTALL_DIR/venv/bin/python3" -c 'import aioesphomeapi, zeroconf' 2>/dev/null; then
    echo "✓ Python environment ready (deps already present)"
else
    echo "  installing dependencies..."
    if [ -x "$USER_HOME/.local/bin/uv" ]; then
        sudo -u "$REAL_USER" "$USER_HOME/.local/bin/uv" pip install --quiet \
            --python "$INSTALL_DIR/venv/bin/python3" -r "$INSTALL_DIR/requirements.txt"
    else
        sudo -u "$REAL_USER" "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"
    fi
    sudo -u "$REAL_USER" "$INSTALL_DIR/venv/bin/python3" -c 'import aioesphomeapi, zeroconf'
    echo "✓ Python environment ready"
fi

# 3. Retire the old user LaunchAgent + tmux session, if present
launchctl bootout "gui/$(id -u "$REAL_USER")/com.erictran.water-monitor" 2>/dev/null || true
rm -f "$USER_HOME/Library/LaunchAgents/$PLIST_NAME"
sudo -u "$REAL_USER" /opt/homebrew/bin/tmux kill-session -t water-monitor 2>/dev/null || true

# 4. Install as a system LaunchDaemon
launchctl bootout "system/com.erictran.water-monitor" 2>/dev/null || true
cp "$INSTALL_DIR/$PLIST_NAME" "$PLIST_DEST"
chown root:wheel "$PLIST_DEST"
chmod 644 "$PLIST_DEST"
launchctl bootstrap system "$PLIST_DEST"
echo "✓ LaunchDaemon installed and started"

sleep 8
echo ""
echo "=== Status ==="
bash "$INSTALL_DIR/status.sh"
