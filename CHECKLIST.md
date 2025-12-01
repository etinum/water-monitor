# Water Level Monitor - Setup Checklist

Use this checklist to ensure your water monitor is properly set up and working.

## ☐ Hardware Setup

- [ ] Float switch acquired (normally open type)
- [ ] Raspberry Pi ready and accessible
- [ ] Jumper wires available (2 wires needed)
- [ ] Float switch connected to GPIO 17
- [ ] Float switch connected to GND
- [ ] Wiring verified against WIRING.md
- [ ] Float switch installed in water container
- [ ] Float switch can move freely up and down

## ☐ Software Installation

- [ ] Files copied to Raspberry Pi at `/home/erictran/Script/water-monitor/`
- [ ] Python 3 installed (should be default on Raspberry Pi OS)
- [ ] RPi.GPIO library installed (`sudo apt-get install python3-rpi.gpio`)
- [ ] Scripts made executable (`chmod +x *.py *.sh`)
- [ ] Log directory created (`mkdir -p /home/erictran/Script`)

## ☐ Email Configuration

- [ ] Gmail account available
- [ ] 2-Factor Authentication enabled on Gmail
- [ ] Gmail App Password created (16 characters)
- [ ] `config.py` updated with EMAIL_FROM
- [ ] `config.py` updated with EMAIL_PASSWORD
- [ ] `config.py` updated with EMAIL_TO
- [ ] Email configuration tested (`python3 test_email.py`)
- [ ] Test email received in inbox

## ☐ Hardware Testing

- [ ] Float switch test run (`python3 test_water_monitor.py`)
- [ ] GPIO reads HIGH when float is UP
- [ ] GPIO reads LOW when float is DOWN
- [ ] Readings are stable (not flickering)
- [ ] Float movement is smooth and reliable

## ☐ System Testing

- [ ] Manual test email sent (`python3 manual_test.py`)
- [ ] Main monitor runs without errors (`python3 water_monitor.py`)
- [ ] Low water alert triggered when float is down
- [ ] Restoration alert triggered when float is up
- [ ] Log file created at `/home/erictran/Script/water_monitor.log`
- [ ] Log entries are readable and make sense

## ☐ Service Installation (Optional but Recommended)

- [ ] Service file copied (`sudo cp water-monitor.service /etc/systemd/system/`)
- [ ] Systemd reloaded (`sudo systemctl daemon-reload`)
- [ ] Service enabled (`sudo systemctl enable water-monitor.service`)
- [ ] Service started (`sudo systemctl start water-monitor.service`)
- [ ] Service status checked (`sudo systemctl status water-monitor.service`)
- [ ] Service shows "active (running)"
- [ ] Service logs accessible (`sudo journalctl -u water-monitor.service`)

## ☐ Final Verification

- [ ] System runs for 10 minutes without errors
- [ ] Low water alert received when tested
- [ ] Restoration alert received when tested
- [ ] Email cooldown working (no spam)
- [ ] Debounce working (no false alarms)
- [ ] Logs show expected behavior
- [ ] Service survives reboot (if installed as service)

## ☐ Documentation Review

- [ ] README.md read and understood
- [ ] QUICKSTART.md reviewed
- [ ] WIRING.md verified against actual wiring
- [ ] PROJECT_SUMMARY.md reviewed for overview
- [ ] Know how to check logs
- [ ] Know how to restart service
- [ ] Know how to troubleshoot common issues

## ☐ Customization (Optional)

- [ ] Check interval adjusted if needed
- [ ] Debounce time adjusted if needed
- [ ] Email cooldown adjusted if needed
- [ ] Restoration alerts enabled/disabled as preferred
- [ ] Detailed logging enabled/disabled as preferred
- [ ] GPIO pin changed if needed

## ☐ Maintenance Plan

- [ ] Monthly float switch test scheduled
- [ ] Quarterly email test scheduled
- [ ] Log rotation configured (optional)
- [ ] Backup plan for email credentials
- [ ] Know how to update software
- [ ] Emergency contact list created

## Troubleshooting Checklist

If something isn't working, check these in order:

### Email Issues
1. [ ] Run `python3 test_email.py`
2. [ ] Verify Gmail App Password is correct (16 chars, no spaces)
3. [ ] Check 2FA is enabled on Gmail
4. [ ] Check spam folder
5. [ ] Verify internet connectivity on Pi
6. [ ] Check SMTP settings in config.py

### Float Switch Issues
1. [ ] Run `python3 test_water_monitor.py`
2. [ ] Verify wiring (GPIO 17 and GND)
3. [ ] Check float switch type (should be normally open)
4. [ ] Test float movement manually
5. [ ] Check for loose connections
6. [ ] Verify GPIO pin number in config.py

### Service Issues
1. [ ] Check service status: `sudo systemctl status water-monitor.service`
2. [ ] View logs: `sudo journalctl -u water-monitor.service -n 50`
3. [ ] Try running manually: `python3 water_monitor.py`
4. [ ] Check file permissions: `ls -la /home/erictran/Script/water-monitor/`
5. [ ] Verify service file paths are correct
6. [ ] Restart service: `sudo systemctl restart water-monitor.service`

## Quick Commands Reference

```bash
# Test email
python3 test_email.py

# Test float switch
python3 test_water_monitor.py

# Send manual test email
python3 manual_test.py

# Run monitor manually
python3 water_monitor.py

# Service commands
sudo systemctl start water-monitor.service
sudo systemctl stop water-monitor.service
sudo systemctl restart water-monitor.service
sudo systemctl status water-monitor.service

# View logs
sudo journalctl -u water-monitor.service -f
tail -f /home/erictran/Script/water_monitor.log
```

## Success Criteria

Your water monitor is successfully set up when:

✓ Float switch readings are correct and stable
✓ Test emails are received within 1 minute
✓ Low water alerts are sent when float is down
✓ Restoration alerts are sent when float is up
✓ No false alarms or spam emails
✓ Service runs continuously without errors
✓ Logs show expected behavior
✓ System survives reboots (if using service)

## Next Steps After Setup

1. **Monitor for a few days** - Watch logs to ensure stable operation
2. **Test in real conditions** - Let water level drop naturally and verify alert
3. **Adjust settings** - Fine-tune intervals and thresholds as needed
4. **Document your setup** - Note any customizations you made
5. **Share feedback** - Report any issues or improvements

## Support

If you complete this checklist and still have issues:

1. Review the log files for error messages
2. Check the troubleshooting section in README.md
3. Verify all wiring connections
4. Test each component individually
5. Try running in manual mode first before using service

---

**Date Completed:** _______________

**Tested By:** _______________

**Notes:** _______________________________________________

_______________________________________________________

_______________________________________________________
