# Water Level Monitor for Raspberry Pi

A Python-based water level monitoring system that uses a float switch to detect low water levels and sends email alerts.

## Hardware Requirements

- Raspberry Pi (any model with GPIO)
- Float switch (normally open)
- Jumper wires

## Wiring Diagram

```
Float Switch Wiring:
- Float Switch Pin 1 → GPIO 17 (BCM numbering)
- Float Switch Pin 2 → GND

How it works:
- When water level is OK: Float is UP → Switch is OPEN → GPIO reads HIGH (1)
- When water level is LOW: Float is DOWN → Switch CLOSES to GND → GPIO reads LOW (0)
```

## Features

- **Real-time monitoring**: Continuously monitors water level via float switch
- **Email alerts**: Sends email notifications when water is low
- **Debounce protection**: Prevents false alarms with configurable debounce time
- **Email cooldown**: Prevents spam with configurable cooldown period
- **Restoration alerts**: Optional notification when water level is restored
- **Detailed logging**: Logs all events to file for troubleshooting
- **Systemd service**: Can run automatically on boot

## Installation

### 1. Clone or copy the project to your Raspberry Pi

```bash
# Copy to your Pi's home directory
scp -r water-monitor pi@your-pi-ip:/home/erictran/Script/
```

### 2. Install required Python packages

```bash
cd /home/erictran/Script/water-monitor
sudo apt-get update
sudo apt-get install python3-rpi.gpio
```

### 3. Configure email settings

Edit `config.py` and update the email configuration:

```python
EMAIL_FROM = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Gmail App Password
EMAIL_TO = ["recipient@example.com"]
```

**Gmail Setup:**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to https://myaccount.google.com/security
3. Create an App Password for "Mail"
4. Use the 16-character app password in config.py

### 4. Test the setup

```bash
# Test email notifications
python3 test_email.py

# Test float switch reading
python3 test_water_monitor.py
```

## Usage

### Run manually

```bash
python3 water_monitor.py
```

### Run as a service (recommended)

```bash
# Copy service file
sudo cp water-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable water-monitor.service

# Start the service
sudo systemctl start water-monitor.service

# Check status
sudo systemctl status water-monitor.service

# View logs
sudo journalctl -u water-monitor.service -f
```

## Configuration

Edit `config.py` to customize settings:

### Hardware Settings
- `FLOAT_PIN`: GPIO pin number (BCM numbering) - default: 17

### Monitoring Settings
- `CHECK_INTERVAL`: Seconds between checks - default: 5
- `DEBOUNCE_TIME`: Seconds to confirm low water - default: 2

### Email Settings
- `EMAIL_NOTIFICATIONS_ENABLED`: Enable/disable emails - default: True
- `EMAIL_COOLDOWN_MINUTES`: Minutes between alerts - default: 30
- `ALERT_ON_LOW_WATER`: Send alert when water is low - default: True
- `ALERT_ON_WATER_RESTORED`: Send alert when restored - default: True

### Logging Settings
- `LOG_FILE`: Path to log file
- `ENABLE_DETAILED_LOGGING`: Enable verbose logging - default: True

## Troubleshooting

### Float switch not working
1. Run `test_water_monitor.py` to see GPIO readings
2. Verify wiring: GPIO 17 and GND
3. Check float switch is normally open type
4. Test by manually moving the float up and down

### Email not sending
1. Run `test_email.py` to test email configuration
2. Verify Gmail App Password is correct
3. Check 2-Factor Authentication is enabled
4. Verify internet connectivity on Pi

### Service not starting
```bash
# Check service status
sudo systemctl status water-monitor.service

# View detailed logs
sudo journalctl -u water-monitor.service -n 50

# Check file permissions
ls -la /home/erictran/Script/water-monitor/
```

## Log Files

- Main log: `/home/erictran/Script/water_monitor.log`
- Service logs: `sudo journalctl -u water-monitor.service`

## Email Alert Examples

### Low Water Alert
```
Subject: ⚠️ ALERT: Water Level is LOW

WARNING: Water level has dropped below the safe threshold!

The float switch has detected low water for more than 2 seconds.
Please refill the water container as soon as possible.
```

### Water Restored Alert
```
Subject: ✓ Water Level Restored

Good news! The water level has been restored to normal.

The float switch indicates the water container has been refilled.
System is now operating normally.
```

## Customization

### Change GPIO Pin
Edit `config.py`:
```python
FLOAT_PIN = 27  # Change to your desired GPIO pin
```

### Adjust Sensitivity
Edit `config.py`:
```python
DEBOUNCE_TIME = 5  # Wait 5 seconds before confirming low water
CHECK_INTERVAL = 10  # Check every 10 seconds
```

### Disable Restoration Alerts
Edit `config.py`:
```python
ALERT_ON_WATER_RESTORED = False
```

## Safety Notes

- The float switch should be normally open (NO)
- GPIO 17 uses internal pull-up resistor
- System is designed to fail-safe (will alert if switch fails)
- Test thoroughly before relying on alerts

## License

Free to use and modify for personal projects.

## Support

For issues or questions, check the log files first:
```bash
tail -f /home/erictran/Script/water_monitor.log
```
