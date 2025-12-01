# Quick Start Guide - Water Level Monitor

## Hardware Setup (5 minutes)

1. **Connect the float switch to your Raspberry Pi:**
   ```
   Float Switch Pin 1 → GPIO 17 (Physical Pin 11)
   Float Switch Pin 2 → GND (Physical Pin 9)
   ```

2. **Float switch logic:**
   - Water OK: Float UP → Switch OPEN → GPIO reads HIGH
   - Water LOW: Float DOWN → Switch CLOSED → GPIO reads LOW

## Software Setup (10 minutes)

### 1. Copy files to Raspberry Pi
```bash
scp -r water-monitor pi@your-pi-ip:/home/erictran/Script/
```

### 2. Run setup script
```bash
cd /home/erictran/Script/water-monitor
chmod +x setup.sh
./setup.sh
```

### 3. Configure email (if not already done)
Edit `config.py`:
```python
EMAIL_FROM = "your-email@gmail.com"
EMAIL_PASSWORD = "your-16-char-app-password"
EMAIL_TO = ["recipient@example.com"]
```

## Testing (5 minutes)

### Test email
```bash
python3 test_email.py
```

### Test float switch
```bash
python3 test_water_monitor.py
# Move the float up and down to see readings change
# Ctrl+C to stop
```

## Run the Monitor

### Option 1: Run manually (for testing)
```bash
python3 water_monitor.py
```

### Option 2: Run as service (recommended)
```bash
# Install service
sudo cp water-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable water-monitor.service
sudo systemctl start water-monitor.service

# Check status
sudo systemctl status water-monitor.service

# View live logs
sudo journalctl -u water-monitor.service -f
```

## Common Commands

```bash
# Start service
sudo systemctl start water-monitor.service

# Stop service
sudo systemctl stop water-monitor.service

# Restart service
sudo systemctl restart water-monitor.service

# Check status
sudo systemctl status water-monitor.service

# View logs (last 50 lines)
sudo journalctl -u water-monitor.service -n 50

# Follow logs in real-time
sudo journalctl -u water-monitor.service -f

# View log file
tail -f /home/erictran/Script/water_monitor.log
```

## Troubleshooting

### No email received?
1. Check email config in `config.py`
2. Run `python3 test_email.py`
3. Verify Gmail App Password is correct
4. Check spam folder

### Float switch not working?
1. Run `python3 test_water_monitor.py`
2. Verify wiring (GPIO 17 and GND)
3. Test by moving float manually
4. Check GPIO pin number in `config.py`

### Service won't start?
```bash
# Check service logs
sudo journalctl -u water-monitor.service -n 50

# Check file permissions
ls -la /home/erictran/Script/water-monitor/

# Test manually first
python3 water_monitor.py
```

## What to Expect

### Normal Operation
- Monitor checks water level every 5 seconds
- Logs "Water level OK" (if detailed logging enabled)
- No emails sent when water is normal

### Low Water Detected
1. Float drops → GPIO reads LOW
2. System waits 2 seconds (debounce)
3. If still low → Logs warning
4. Sends email alert
5. Won't send another email for 30 minutes (cooldown)

### Water Restored
1. Float rises → GPIO reads HIGH
2. Logs "Water level restored"
3. Sends restoration email (if enabled)
4. Returns to normal monitoring

## Customization

### Change check frequency
Edit `config.py`:
```python
CHECK_INTERVAL = 10  # Check every 10 seconds instead of 5
```

### Disable restoration emails
Edit `config.py`:
```python
ALERT_ON_WATER_RESTORED = False
```

### Change cooldown period
Edit `config.py`:
```python
EMAIL_COOLDOWN_MINUTES = 60  # Wait 1 hour between alerts
```

## Need Help?

1. Check the main README.md for detailed documentation
2. View logs: `tail -f /home/erictran/Script/water_monitor.log`
3. Test components individually with test scripts
