#!/usr/bin/env python3
"""
Configuration for the water monitor server (runs on the Mac mini)
"""

# ESP32 sensor (ESPHome native API)
SENSOR_HOST = "water-sensor.local"  # falls back to IP below if mDNS fails
SENSOR_HOST_FALLBACK = "192.168.1.213"
SENSOR_PORT = 6053
API_ENCRYPTION_KEY = "cN6BW3ebipgdymPWTCiz+or8BKAXNwIXZGdBnNH9478="

# The binary sensor object_id in the ESPHome config
WATER_SENSOR_OBJECT_ID = "water_low"

# Offline detection: alert if the ESP32 stays unreachable this long
OFFLINE_ALERT_MINUTES = 10
ALERT_ON_SENSOR_OFFLINE = True
ALERT_ON_SENSOR_ONLINE = True  # send all-clear when it comes back

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
LOG_FILE = "/Users/erictran/Script/water-monitor/water_monitor.log"
ENABLE_DETAILED_LOGGING = True

# Alert Settings
ALERT_ON_LOW_WATER = True
ALERT_ON_WATER_RESTORED = True

# Weekly Summary Settings
WEEKLY_SUMMARY_ENABLED = True
WEEKLY_SUMMARY_DAY = 0  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
WEEKLY_SUMMARY_HOUR = 8  # Hour of the day to send summary (0-23 in local time)
