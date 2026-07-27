#!/bin/bash
# Quick health check for the water monitoring system (run on the Mac mini)
# Usage: bash ~/Script/water-monitor/status.sh
INSTALL_DIR="/Users/erictran/Script/water-monitor"
TMUX_BIN=/opt/homebrew/bin/tmux

echo "════════════════════════════════════════════════"
echo " Water Monitor Status — $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════"

echo ""
echo "── Server (tmux session) ──"
if $TMUX_BIN has-session -t water-monitor 2>/dev/null; then
    echo "tmux session: RUNNING  →  watch live: tmux attach -t water-monitor"
    pgrep -fl water_server.py | head -1 || echo "  (session exists but python not running — check the pane) ⚠️"
else
    echo "tmux session: NOT RUNNING ⚠️  (launchd re-creates it within 5 min, or run: bash $INSTALL_DIR/run_server.sh)"
fi

echo ""
echo "── ESP32 sensor ──"
if nc -z -G 2 water-sensor.local 6053 2>/dev/null; then
    echo "water-sensor.local: REACHABLE (API port 6053 open)"
else
    echo "water-sensor.local: UNREACHABLE ⚠️"
fi

echo ""
echo "── Last 15 log lines ──"
tail -15 "$INSTALL_DIR/water_monitor.log" 2>/dev/null || echo "(no log yet)"
