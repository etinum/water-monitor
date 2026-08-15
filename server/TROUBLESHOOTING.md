# Troubleshooting

## `No route to host` (Errno 65) while the sensor is provably reachable

**Symptom.** `water_monitor.log` fills with, once a minute, forever:

```
Failed to connect to ESP32 sensor: Error connecting to [AddrInfo(... address='192.168.1.207', port=6053)]: [Errno 65] No route to host
```

Meanwhile `ping water-sensor.local` works, `nc -z water-sensor.local 6053` succeeds, and
connecting by hand over SSH works fine. The old `status.sh` reported the sensor
"REACHABLE" in the same second the server logged a failure.

A second, decisive tell — the server also fails to send mDNS multicast on *every*
interface at startup:

```
Error with socket 11 (('192.168.1.202', 5353))): [Errno 65] No route to host
Error with socket 13 (('192.168.1.17', 5353))): [Errno 65] No route to host
```

**Cause.** macOS 15+ Local Network Privacy. It silently denies local-subnet traffic
(both TCP and mDNS multicast) to processes launched by launchd in the *user* domain.
It is not a network fault, not the IP, not mDNS, and not the ESP32.

The trap: the binaries here (Homebrew `tmux`, uv-managed `python3`) are **ad-hoc
signed with no stable identity** — `tmux-5555...`, and python's `Identifier=-`. macOS
never registers them in System Settings → Privacy & Security → Local Network, so
**there is no entry to toggle on**, and no permission prompt is ever shown. The denial
is not logged anywhere either.

**Diagnosis.** The same binary succeeds or fails purely by launch context:

| Launched from | Result |
|---|---|
| SSH session (child of `sshd`, a root system daemon) | works |
| Terminal.app, after granting it Local Network | works |
| launchd user LaunchAgent → tmux → python | **EHOSTUNREACH** |
| launchd user LaunchAgent → python directly | **EHOSTUNREACH** |
| **system LaunchDaemon (root)** | **works — exempt** |

Granting Terminal.app permission does *not* help the service: TCC attributes the grant
to the responsible app (Terminal), and the launchd-spawned tmux server has its own
unregistrable identity.

**Fix.** Run the server as a system LaunchDaemon in `/Library/LaunchDaemons`, owned
`root:wheel` — system-domain daemons are exempt from Local Network Privacy. This is why
`install_server.sh` requires sudo and why tmux was removed (launchd `KeepAlive` replaces
the old tmux watchdog loop).

**Do not** "fix" this by moving back to a user LaunchAgent, or by re-adding tmux.

### What triggered it

The Mac mini rebooted on 2026-08-14 around 10:55. The service came back under the user
LaunchAgent and was denied from that moment. It ran, logged, and heartbeated normally for
24 hours while being completely blind — a fresh restart of the process did not fix it,
because the block is external to the process.

### Side effect worth recognising

With no API client connected, the ESP32 reboots every ~15 minutes (ESPHome's default
`api: reboot_timeout`). A sensor whose `uptime` is always under 15 minutes is a symptom of
*nothing connecting to it*, not of a flaky sensor. It resolves itself once the server
reconnects.

## Checking real health

`nc`/`ping` reachability is **not** health — it was green throughout the outage above.
The real indicators:

```bash
bash ~/Script/water-monitor/status.sh        # flags recent 'No route to host'
sudo launchctl print system/com.erictran.water-monitor | head -20
tail -f ~/Script/water-monitor/water_monitor.log
```

A healthy log shows `heartbeat: water OK, sensor connected` hourly. If it instead shows
`heartbeat: sensor OFFLINE for Nm`, the server is running but blind.
