# Deployment Guide — Water Level Monitor

Current architecture (since 2026-07): an **ESP32** running ESPHome reads the float switch
and exposes it over the ESPHome native API; a **Mac mini** runs `water_server.py`, which
holds a persistent connection to the sensor and sends email alerts.

The Raspberry Pi deployment was decommissioned in 2026-07. `water_monitor.py`,
`water-monitor.service`, `setup.sh` and the `test_*.py` helpers at the repo root are Pi-era
files kept for reference; they are not part of the running system.

| | |
|---|---|
| Sensor | `water-sensor.local` (192.168.1.207), ESP32 + ESPHome, float switch on GPIO4 |
| Server | Mac mini — `ETMiniM1.local`, user `erictran` |
| Install dir | `/Users/erictran/Script/water-monitor` |
| Service | `com.erictran.water-monitor`, a **system LaunchDaemon** |
| Source | `server/` (Mac mini), `esp32/` (firmware) |

## Deploying the server

From this repo on your Mac:

```bash
cd server
scp water_server.py config.py requirements.txt status.sh install_server.sh \
    com.erictran.water-monitor.plist TROUBLESHOOTING.md \
    erictran@ETMiniM1.local:/Users/erictran/Script/water-monitor/
```

Then on the mini (the installer **requires sudo** — see the warning below):

```bash
cd ~/Script/water-monitor && sudo bash install_server.sh
```

The installer is idempotent. It creates the venv if missing, installs dependencies only
when they don't already import, retires any old user LaunchAgent and tmux session, then
installs and bootstraps the LaunchDaemon and prints status.

For a code-only change you can skip the full install and just restart:

```bash
sudo launchctl kickstart -k system/com.erictran.water-monitor
```

## ⚠️ It must be a system LaunchDaemon — not a user LaunchAgent

This is the single most important fact about this deployment.

macOS 15+ **Local Network Privacy** silently denies local-subnet traffic (TCP *and* mDNS)
to processes launched by launchd in the *user* domain. The binaries involved (Homebrew
`tmux`, uv-managed `python3`) are ad-hoc signed with no stable identity, so they never
appear in System Settings → Privacy & Security → Local Network — there is **no permission
to grant**, and no prompt is ever shown. System-domain daemons are exempt.

Running it as a LaunchAgent produces a server that starts fine, logs fine, heartbeats
fine, and is completely blind — `[Errno 65] No route to host` against a sensor that
`ping` and `nc` both report as perfectly reachable. This caused ~24 hours of undetected
downtime on 2026-08-14.

Full diagnosis, including the launch-context comparison table: **`server/TROUBLESHOOTING.md`**.

## Verifying

```bash
bash ~/Script/water-monitor/status.sh
```

A healthy system shows `process: RUNNING`, `✓ connected`, and hourly log lines like:

```
heartbeat: water OK, sensor connected, wifi <SSID> via AP <BSSID> @ -59 dBm
```

Do **not** treat `ping`/`nc` reachability as health — it stayed green for the entire
2026-08-14 outage. The connection state line and the heartbeat are the real indicators.

Useful commands:

```bash
tail -f ~/Script/water-monitor/water_monitor.log      # application log
tail -f ~/Script/water-monitor/server.err.log         # daemon stdout/stderr
sudo launchctl print system/com.erictran.water-monitor
```

### Verify after reboot

The daemon is `RunAtLoad` + `KeepAlive` in `/Library/LaunchDaemons`, so it starts at boot
**without requiring anyone to log in** — unlike the old LaunchAgent, which needed a GUI
login session. After any reboot:

```bash
bash ~/Script/water-monitor/status.sh
```

If it does not come up, check that the plist is still `root:wheel` in
`/Library/LaunchDaemons` and consult `server/TROUBLESHOOTING.md` before changing anything.

## Deploying firmware to the ESP32

From `esp32/` (requires `esphome`, and `secrets.yaml` which is gitignored):

```bash
esphome run water-sensor.yaml
```

OTA is enabled, so the device does not need to be plugged in after the first flash.

Note: with no `reboot_timeout` set in the `api:` block, ESPHome's default applies — the
ESP32 **reboots every 15 minutes if no API client is connected**. A sensor whose uptime
never exceeds 15 minutes is a symptom of the server not connecting, not a flaky sensor.

## Uninstall

```bash
sudo launchctl bootout system/com.erictran.water-monitor
sudo rm /Library/LaunchDaemons/com.erictran.water-monitor.plist
rm -rf ~/Script/water-monitor
```
