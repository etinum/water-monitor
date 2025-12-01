# Deployment Guide - Water Level Monitor

## Quick Deploy to Raspberry Pi

### Step 1: Copy Files to Raspberry Pi

From your Mac, run:

```bash
# Navigate to the project directory
cd /Users/erictran/rpi/water-monitor

# Copy entire directory to Raspberry Pi
# Replace 'pi-hostname' with your Pi's IP address or hostname
scp -r . pi@pi-hostname:/home/erictran/Script/water-monitor/

# Or if you're using a specific user:
scp -r . erictran@pi-hostname:/home/erictran/Script/water-monitor/
```

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@pi-hostname
# or
ssh erictran@pi-hostname
```

### Step 3: Run Setup Script

```bash
cd /home/erictran/Script/water-monitor
chmod +x setup.sh
./setup.sh
```

This will:
- Install Python GPIO library
- Create log directory
- Make scripts executable
- Test email configuration

### Step 4: Configure Email (if needed)

Edit the config file:
```bash
nano config.py
```

Update these lines:
```python
EMAIL_FROM = "your-email@gmail.com"
EMAIL_PASSWORD = "your-16-char-app-password"
EMAIL_TO = ["recipient@example.com"]
```

Save and exit (Ctrl+X, Y, Enter)

### Step 5: Test Everything

```bash
# Test email
python3 test_email.py

# Test float switch (move float up and down)
python3 test_water_monitor.py
# Press Ctrl+C to stop

# Send manual test email
python3 manual_test.py
```

### Step 6: Install as Service (Recommended)

```bash
# Copy service file
sudo cp water-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable water-monitor.service

# Start service now
sudo systemctl start water-monitor.service

# Check status
sudo systemctl status water-monitor.service
```

### Step 7: Verify Service is Running

```bash
# Should show "active (running)"
sudo systemctl status water-monitor.service

# Watch logs in real-time
sudo journalctl -u water-monitor.service -f
# Press Ctrl+C to stop watching
```

## Alternative: Manual Deployment

If you prefer to deploy manually:

### 1. Create Directory
```bash
ssh pi@pi-hostname
mkdir -p /home/erictran/Script/water-monitor
cd /home/erictran/Script/water-monitor
```

### 2. Copy Files One by One
```bash
# From your Mac, in separate terminal
cd /Users/erictran/rpi/water-monitor

scp config.py pi@pi-hostname:/home/erictran/Script/water-monitor/
scp water_monitor.py pi@pi-hostname:/home/erictran/Script/water-monitor/
scp test_water_monitor.py pi@pi-hostname:/home/erictran/Script/water-monitor/
scp test_email.py pi@pi-hostname:/home/erictran/Script/water-monitor/
scp manual_test.py pi@pi-hostname:/home/erictran/Script/water-monitor/
scp setup.sh pi@pi-hostname:/home/erictran/Script/water-monitor/
scp water-monitor.service pi@pi-hostname:/home/erictran/Script/water-monitor/
scp README.md pi@pi-hostname:/home/erictran/Script/water-monitor/
```

### 3. Make Executable
```bash
# On Raspberry Pi
cd /home/erictran/Script/water-monitor
chmod +x *.py *.sh
```

### 4. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio
```

### 5. Continue with Step 4 above

## Updating Existing Installation

If you already have the monitor installed and want to update:

```bash
# From your Mac
cd /Users/erictran/rpi/water-monitor
scp water_monitor.py pi@pi-hostname:/home/erictran/Script/water-monitor/

# On Raspberry Pi
ssh pi@pi-hostname
sudo systemctl restart water-monitor.service
```

## Deployment Checklist

- [ ] Files copied to Pi
- [ ] Dependencies installed
- [ ] Email configured
- [ ] Email test passed
- [ ] Float switch test passed
- [ ] Service installed
- [ ] Service running
- [ ] Logs showing normal operation

## Troubleshooting Deployment

### Can't connect to Pi
```bash
# Find Pi on network
ping raspberrypi.local

# Or scan network
nmap -sn 192.168.1.0/24
```

### Permission denied
```bash
# On Pi, fix permissions
sudo chown -R erictran:erictran /home/erictran/Script/water-monitor
chmod +x /home/erictran/Script/water-monitor/*.py
```

### Service won't start
```bash
# Check logs
sudo journalctl -u water-monitor.service -n 50

# Verify paths in service file
cat /etc/systemd/system/water-monitor.service

# Test manually first
cd /home/erictran/Script/water-monitor
python3 water_monitor.py
```

### GPIO permission denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio erictran

# Reboot
sudo reboot
```

## Post-Deployment

### Monitor for First 24 Hours

```bash
# Watch logs
sudo journalctl -u water-monitor.service -f

# Check log file
tail -f /home/erictran/Script/water_monitor.log
```

### Test Low Water Alert

1. Manually lower the float switch
2. Wait 2 seconds (debounce time)
3. Check email for alert
4. Raise float switch
5. Check email for restoration alert

### Verify After Reboot

```bash
# Reboot Pi
sudo reboot

# After reboot, check service
sudo systemctl status water-monitor.service

# Should show "active (running)"
```

## Production Recommendations

1. **Use static IP** for your Raspberry Pi
2. **Set up SSH keys** for passwordless login
3. **Configure log rotation** to prevent disk fill
4. **Test monthly** to ensure system is working
5. **Keep backups** of config.py (without passwords)
6. **Document** any customizations you make

## Uninstall

If you need to remove the water monitor:

```bash
# Stop and disable service
sudo systemctl stop water-monitor.service
sudo systemctl disable water-monitor.service

# Remove service file
sudo rm /etc/systemd/system/water-monitor.service

# Reload systemd
sudo systemctl daemon-reload

# Remove files
rm -rf /home/erictran/Script/water-monitor

# Remove log file
rm /home/erictran/Script/water_monitor.log
```

## Support

After deployment, refer to:
- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick reference
- **CHECKLIST.md** - Verification steps
- **Log files** - For troubleshooting

---

**Deployment Date:** _______________

**Pi Hostname/IP:** _______________

**Notes:** _______________________________________________
