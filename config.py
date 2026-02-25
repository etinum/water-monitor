#!/usr/bin/env python3
"""
Configuration file for water level monitor
"""

# Hardware Configuration
FLOAT_PIN = 17  # GPIO pin for float switch (BCM numbering)

# Monitoring Settings
CHECK_INTERVAL = 5  # Seconds between water level checks
DEBOUNCE_TIME = 15  # Seconds to wait before confirming low water state (prevents false alarms)

# Email Configuration (Gmail setup)
EMAIL_NOTIFICATIONS_ENABLED = True
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "eric.n.tran@gmail.com"
EMAIL_PASSWORD = "qkiu pjeu vogc wedr"  # Gmail App Password
EMAIL_TO = ["eric.n.tran@gmail.com"]

# Email notification cooldown (prevent spam)
EMAIL_COOLDOWN_MINUTES = 30  # Wait 30 minutes between low water alerts

# Logging Configuration
LOG_FILE = "/home/pi/Script/water_monitor.log"
ENABLE_DETAILED_LOGGING = True

# Alert Settings
ALERT_ON_LOW_WATER = True
ALERT_ON_WATER_RESTORED = True  # Send email when water level returns to normal

# Weekly Summary Settings
WEEKLY_SUMMARY_ENABLED = True
WEEKLY_SUMMARY_DAY = 0  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
WEEKLY_SUMMARY_HOUR = 8  # Hour of the day to send summary (0-23 in local time)
