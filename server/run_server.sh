#!/bin/bash
# Ensure the water monitor server is running inside a tmux session.
# Called by the com.erictran.water-monitor LaunchAgent (at login + every 5 min).
# Idempotent: exits immediately if the session already exists.
# Watch it live:  tmux attach -t water-monitor   (detach with ctrl-b d)

TMUX_BIN=/opt/homebrew/bin/tmux
SESSION=water-monitor
DIR=/Users/erictran/Script/water-monitor

$TMUX_BIN has-session -t $SESSION 2>/dev/null && exit 0

# Inner while-loop restarts the server if it ever crashes/exits
$TMUX_BIN new-session -d -s $SESSION -c "$DIR" \
  '/bin/bash -c "while true; do venv/bin/python3 -u water_server.py; echo; echo \"[watchdog] server exited (code $?) — restarting in 10s\"; sleep 10; done"'
