# Water Level Monitor - Project Summary

## Overview
A Raspberry Pi-based water level monitoring system that uses a float switch on GPIO 17 to detect low water levels and sends email alerts via Gmail.

## Project Structure

```
water-monitor/
├── water_monitor.py          # Main monitoring script
├── config.py                  # Configuration settings
├── test_water_monitor.py      # Test float switch GPIO reading
├── test_email.py              # Test email notifications
├── manual_test.py             # Send test email on demand
├── setup.sh                   # Automated setup script
├── water-monitor.service      # Systemd service file
├── README.md                  # Complete documentation
├── QUICKSTART.md              # Quick start guide
├── WIRING.md                  # Detailed wiring guide
├── PROJECT_SUMMARY.md         # This file
└── .gitignore                 # Git ignore file
```

## Key Features

### 1. Hardware Monitoring
- **GPIO Pin:** 17 (BCM numbering)
- **Float Switch:** Normally open type
- **Pull-up resistor:** Internal (configured in software)
- **Logic:**
  - HIGH (1) = Water OK (float up)
  - LOW (0) = Water LOW (float down)

### 2. Email Alerts
- **Provider:** Gmail SMTP
- **Low water alert:** Sent when water drops below threshold
- **Restoration alert:** Sent when water level returns to normal
- **Cooldown:** 30 minutes between alerts (configurable)
- **Debounce:** 2 seconds to confirm low water (prevents false alarms)

### 3. Logging
- **Log file:** `/home/erictran/Script/water_monitor.log`
- **System logs:** Available via journalctl
- **Detailed logging:** Configurable on/off

### 4. Service Management
- **Systemd service:** Runs automatically on boot
- **Auto-restart:** Restarts if crashed
- **Status monitoring:** Via systemctl commands

## Configuration Options

### Hardware Settings
```python
FLOAT_PIN = 17                    # GPIO pin (BCM)
```

### Monitoring Settings
```python
CHECK_INTERVAL = 5                # Seconds between checks
DEBOUNCE_TIME = 2                 # Seconds to confirm low water
```

### Email Settings
```python
EMAIL_NOTIFICATIONS_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "your-email@gmail.com"
EMAIL_PASSWORD = "app-password"
EMAIL_TO = ["recipient@example.com"]
EMAIL_COOLDOWN_MINUTES = 30
```

### Alert Settings
```python
ALERT_ON_LOW_WATER = True         # Send alert when water is low
ALERT_ON_WATER_RESTORED = True    # Send alert when restored
```

### Logging Settings
```python
LOG_FILE = "/home/erictran/Script/water_monitor.log"
ENABLE_DETAILED_LOGGING = True
```

## Usage Scenarios

### Scenario 1: Testing Setup
```bash
# Test email
python3 test_email.py

# Test float switch
python3 test_water_monitor.py

# Send manual test email
python3 manual_test.py
```

### Scenario 2: Manual Monitoring
```bash
# Run in foreground (see output in terminal)
python3 water_monitor.py
```

### Scenario 3: Production Use
```bash
# Install as service
sudo cp water-monitor.service /etc/systemd/system/
sudo systemctl enable water-monitor.service
sudo systemctl start water-monitor.service

# Monitor logs
sudo journalctl -u water-monitor.service -f
```

## Email Alert Examples

### Low Water Alert
```
Subject: ⚠️ ALERT: Water Level is LOW

WARNING: Water level has dropped below the safe threshold!

The float switch has detected low water for more than 2 seconds.
Please refill the water container as soon as possible.

Action Required:
- Check water container
- Refill water if needed
- Verify float switch is working properly

Timestamp: 2025-11-30 21:14:00
Location: Raspberry Pi Water Monitor
GPIO Pin: 17
```

### Water Restored Alert
```
Subject: ✓ Water Level Restored

Good news! The water level has been restored to normal.

The float switch indicates the water container has been refilled.
System is now operating normally.

Timestamp: 2025-11-30 21:45:00
Location: Raspberry Pi Water Monitor
GPIO Pin: 17
```

## System Behavior

### Normal Operation
1. Check water level every 5 seconds
2. If water OK (GPIO HIGH):
   - Log status (if detailed logging enabled)
   - Continue monitoring
3. If water LOW (GPIO LOW):
   - Start debounce timer
   - Wait 2 seconds
   - If still low, trigger alert

### Low Water Detection
1. Float drops → GPIO reads LOW
2. System waits 2 seconds (debounce)
3. If still low after debounce:
   - Log warning
   - Send email alert
   - Set cooldown timer (30 minutes)
4. Continue monitoring every 5 seconds
5. Won't send another email until cooldown expires

### Water Restoration
1. Float rises → GPIO reads HIGH
2. Log restoration
3. Send restoration email (if enabled)
4. Reset cooldown timer
5. Return to normal monitoring

## Technical Details

### Dependencies
- Python 3
- RPi.GPIO library
- smtplib (built-in)
- email (built-in)

### GPIO Configuration
- Mode: BCM (Broadcom numbering)
- Pin: GPIO 17
- Direction: Input
- Pull: Pull-up (internal)
- Cleanup: Automatic on exit

### Email Configuration
- Protocol: SMTP with STARTTLS
- Server: smtp.gmail.com:587
- Authentication: Gmail App Password
- Format: Plain text with MIME

### Service Configuration
- Type: Simple
- Restart: Always (10 second delay)
- User: erictran
- Working Directory: /home/erictran/Script/water-monitor

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| No email received | Run `test_email.py`, check Gmail App Password |
| Float switch not working | Run `test_water_monitor.py`, verify wiring |
| Service won't start | Check `journalctl -u water-monitor.service` |
| False alarms | Increase `DEBOUNCE_TIME` in config.py |
| Too many emails | Increase `EMAIL_COOLDOWN_MINUTES` |
| Wrong GPIO readings | Verify float switch is normally open type |

## Maintenance

### Regular Checks
- Test float switch monthly (move manually)
- Verify email alerts work (use manual_test.py)
- Check log file size (rotate if needed)
- Review system logs for errors

### Log Rotation
```bash
# Add to /etc/logrotate.d/water-monitor
/home/erictran/Script/water_monitor.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

### Updates
- Pull latest code from repository
- Review config.py for new settings
- Restart service: `sudo systemctl restart water-monitor.service`

## Future Enhancements

Possible improvements:
- [ ] Web dashboard for status monitoring
- [ ] SMS alerts (via Twilio)
- [ ] Multiple float switches for different levels
- [ ] Data logging to database
- [ ] Integration with Home Assistant
- [ ] Push notifications (via Pushover/Telegram)
- [ ] Water usage statistics
- [ ] Predictive alerts based on usage patterns

## Comparison with Battery Monitor

This project is based on the battery monitor project with these key differences:

| Feature | Battery Monitor | Water Monitor |
|---------|----------------|---------------|
| Input | Voltage reading (serial) | GPIO digital input |
| Monitoring | Continuous analog value | Binary state (high/low) |
| Complexity | High (charging logic) | Low (simple detection) |
| Alerts | Multiple thresholds | Single threshold |
| Control | Relay control (output) | Monitoring only (input) |
| Update frequency | 60 seconds | 5 seconds |

## License
Free to use and modify for personal projects.

## Credits
- Based on battery monitor project structure
- Email configuration adapted from battery-monitor/config.py
- GPIO handling follows Raspberry Pi best practices
