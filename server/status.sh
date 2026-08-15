#!/bin/bash
# Quick health check for the water monitoring system (run on the Mac mini)
# Usage: bash ~/Script/water-monitor/status.sh
INSTALL_DIR="/Users/erictran/Script/water-monitor"

echo "════════════════════════════════════════════════"
echo " Water Monitor Status — $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════"

echo ""
echo "── Server (LaunchDaemon) ──"
if pgrep -f water_server.py >/dev/null; then
    echo "process: RUNNING"
    pgrep -fl water_server.py | head -1
else
    echo "process: NOT RUNNING ⚠️"
    echo "  start with: sudo launchctl kickstart -k system/com.erictran.water-monitor"
fi

echo ""
echo "── ESP32 sensor ──"
if nc -z -G 2 water-sensor.local 6053 2>/dev/null; then
    echo "water-sensor.local: port 6053 reachable"
else
    echo "water-sensor.local: UNREACHABLE ⚠️"
fi

# Reachability alone is NOT health: for 24h on 2026-08-14 the port was open while the
# server was blocked by Local Network Privacy. The log below is the real indicator.
echo ""
echo "── Connection state (the line that actually matters) ──"
# Compare the LAST success against the LAST failure by line number, rather than grepping
# a trailing window: after a recovery the window still holds old errors, and a stale
# warning here is exactly as useless as the old "REACHABLE" false-negative.
LOG="$INSTALL_DIR/water_monitor.log"
last_ok=$(grep -n 'Connected to ESP32 sensor' "$LOG" 2>/dev/null | tail -1 | cut -d: -f1)
last_fail=$(grep -n 'No route to host' "$LOG" 2>/dev/null | tail -1 | cut -d: -f1)
if [ -z "$last_ok" ] && [ -z "$last_fail" ]; then
    echo "no connection events in the current log"
elif [ "${last_ok:-0}" -gt "${last_fail:-0}" ]; then
    echo "✓ connected — last event was a successful connect"
else
    echo "⚠️  server cannot reach the sensor ('No route to host')."
    echo "    Confirm it runs as a system LaunchDaemon, not a user LaunchAgent:"
    echo "      ls -l /Library/LaunchDaemons/com.erictran.water-monitor.plist"
    echo "    See TROUBLESHOOTING.md."
fi

echo ""
echo "── Last 15 log lines ──"
tail -15 "$INSTALL_DIR/water_monitor.log" 2>/dev/null || echo "(no log yet)"
