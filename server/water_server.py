#!/usr/bin/env python3
"""
Water Level Monitor Server (Mac mini)
Subscribes to the ESP32 water sensor over the ESPHome native API and sends
email alerts — a port of the Raspberry Pi's water_monitor.py.

The ESP32 does the debouncing (delayed_on: 15s in its firmware), so a state
change arriving here is already confirmed.
"""

import asyncio
import logging
import smtplib
import socket
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging.handlers import TimedRotatingFileHandler

import zeroconf
from aioesphomeapi import APIClient, BinarySensorInfo, BinarySensorState, ReconnectLogic

from config import (
    SENSOR_HOST,
    SENSOR_HOST_FALLBACK,
    SENSOR_PORT,
    API_ENCRYPTION_KEY,
    WATER_SENSOR_OBJECT_ID,
    OFFLINE_ALERT_MINUTES,
    ALERT_ON_SENSOR_OFFLINE,
    ALERT_ON_SENSOR_ONLINE,
    EMAIL_NOTIFICATIONS_ENABLED,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_FROM,
    EMAIL_PASSWORD,
    EMAIL_TO,
    EMAIL_COOLDOWN_MINUTES,
    LOG_FILE,
    ENABLE_DETAILED_LOGGING,
    ALERT_ON_LOW_WATER,
    ALERT_ON_WATER_RESTORED,
    WEEKLY_SUMMARY_ENABLED,
    WEEKLY_SUMMARY_DAY,
    WEEKLY_SUMMARY_HOUR,
)


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if ENABLE_DETAILED_LOGGING else logging.WARNING)
    if logger.hasHandlers():
        logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


class WaterMonitorServer:
    def __init__(self):
        self.last_email_time = None
        self.water_is_low = False

        # Stats for weekly summary
        self.stats_start_time = datetime.now()
        self.low_water_events = 0
        self.emails_sent = 0
        self.last_weekly_summary_date = None

        # Sensor connectivity
        self.sensor_connected = False
        self.disconnected_since = None
        self.offline_alert_sent = False

        self.water_sensor_key = None
        self.entity_ids = {}  # entity key -> object_id
        self.wifi_info = {}   # wifi_ssid / wifi_bssid / wifi_signal / ip_address
        self.client = None
        self.reconnect_logic = None

    # ------------------------------------------------------------------ email

    def can_send_email(self):
        if self.last_email_time is None:
            return True
        return datetime.now() - self.last_email_time >= timedelta(minutes=EMAIL_COOLDOWN_MINUTES)

    def _send_email_sync(self, subject, message):
        msg = MIMEMultipart()
        msg["From"] = EMAIL_FROM
        msg["To"] = ", ".join(EMAIL_TO)
        msg["Subject"] = subject

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"""
{message}

Timestamp: {current_time}
Location: ESP32 Water Sensor (via Mac mini server)

This is an automated alert from your Water Level Monitor.
"""
        msg.attach(MIMEText(full_message, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())
        server.quit()

    async def send_email_notification(self, subject, message):
        if not EMAIL_NOTIFICATIONS_ENABLED:
            logging.info("Email notifications disabled, skipping email")
            return False
        if not EMAIL_FROM or not EMAIL_PASSWORD or not EMAIL_TO:
            logging.warning("Email notifications enabled but credentials not configured")
            return False
        try:
            await asyncio.to_thread(self._send_email_sync, subject, message)
            logging.info(f"Email notification sent: {subject}")
            self.last_email_time = datetime.now()
            self.emails_sent += 1
            return True
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False

    # ------------------------------------------------------------ water state

    async def handle_water_state(self, is_low):
        """Called on every state update of the water_low binary sensor.
        Debounce already happened on the ESP32 (delayed_on: 15s)."""
        if is_low and not self.water_is_low:
            self.water_is_low = True
            self.low_water_events += 1
            logging.warning("⚠️  LOW WATER LEVEL CONFIRMED!")
            if ALERT_ON_LOW_WATER and self.can_send_email():
                subject = "⚠️ ALERT: Water Level is LOW"
                message = """
WARNING: Water level has dropped below the safe threshold!

The float switch has detected low water (confirmed by the sensor's
15-second debounce). Please refill the water container as soon as possible.

Action Required:
- Check water container
- Refill water if needed
- Verify float switch is working properly
"""
                await self.send_email_notification(subject, message)
            else:
                logging.info("Email cooldown active or alerts disabled, skipping notification")

        elif not is_low and self.water_is_low:
            self.water_is_low = False
            logging.info("✓ Water level restored to normal")
            if ALERT_ON_WATER_RESTORED:
                subject = "✓ Water Level Restored"
                message = """
Good news! The water level has been restored to normal.

The float switch indicates the water container has been refilled.
System is now operating normally.
"""
                await self.send_email_notification(subject, message)

    # ------------------------------------------------------ ESPHome connection

    def on_state(self, state):
        if isinstance(state, BinarySensorState) and state.key == self.water_sensor_key:
            asyncio.create_task(self.handle_water_state(state.state))
            return
        obj = self.entity_ids.get(state.key)
        if obj in ("wifi_ssid", "wifi_bssid", "ip_address", "wifi_signal"):
            if not getattr(state, "missing_state", False):
                self.wifi_info[obj] = state.state

    def wifi_summary(self):
        """One-line description of the sensor's WiFi connection, or '' if unknown."""
        if not self.wifi_info:
            return ""
        ssid = self.wifi_info.get("wifi_ssid", "?")
        bssid = self.wifi_info.get("wifi_bssid", "?")
        rssi = self.wifi_info.get("wifi_signal")
        rssi_part = f" @ {rssi:.0f} dBm" if isinstance(rssi, (int, float)) else ""
        return f"wifi {ssid} via AP {bssid}{rssi_part}"

    async def on_connect(self):
        logging.info("Connected to ESP32 sensor")
        was_offline_alerted = self.offline_alert_sent
        self.sensor_connected = True
        self.disconnected_since = None
        self.offline_alert_sent = False

        try:
            entities, _services = await self.client.list_entities_services()
        except Exception as e:
            logging.error(f"Failed to list entities: {e}")
            return

        self.entity_ids = {e.key: e.object_id for e in entities}
        self.water_sensor_key = None
        for entity in entities:
            if isinstance(entity, BinarySensorInfo) and entity.object_id == WATER_SENSOR_OBJECT_ID:
                self.water_sensor_key = entity.key
                break

        if self.water_sensor_key is None:
            logging.error(
                f"Binary sensor '{WATER_SENSOR_OBJECT_ID}' not found on device — check the ESPHome config"
            )
            return

        self.client.subscribe_states(self.on_state)
        logging.info(f"Subscribed to '{WATER_SENSOR_OBJECT_ID}' (key={self.water_sensor_key})")

        if was_offline_alerted and ALERT_ON_SENSOR_ONLINE:
            await self.send_email_notification(
                "✓ Water Sensor Back Online",
                "The ESP32 water sensor has reconnected and monitoring has resumed.",
            )

    async def on_disconnect(self, expected_disconnect=False):
        self.sensor_connected = False
        self.disconnected_since = datetime.now()
        logging.warning(f"Disconnected from ESP32 sensor (expected={expected_disconnect})")

    async def on_connect_error(self, err):
        if self.disconnected_since is None:
            self.disconnected_since = datetime.now()
        logging.warning(f"Failed to connect to ESP32 sensor: {err}")

    # ------------------------------------------------------- background tasks

    async def watchdog_loop(self):
        """Alert if the sensor stays offline too long."""
        while True:
            await asyncio.sleep(30)
            if self.sensor_connected or not ALERT_ON_SENSOR_OFFLINE or self.offline_alert_sent:
                continue
            if self.disconnected_since is None:
                continue
            offline_for = datetime.now() - self.disconnected_since
            if offline_for >= timedelta(minutes=OFFLINE_ALERT_MINUTES):
                minutes = int(offline_for.total_seconds() // 60)
                sent = await self.send_email_notification(
                    "⚠️ ALERT: Water Sensor OFFLINE",
                    f"""
WARNING: The ESP32 water sensor has been unreachable for {minutes} minutes.

Water level is NOT being monitored right now.

Action Required:
- Check the sensor's power supply
- Check WiFi connectivity
- Power-cycle the ESP32 if needed
""",
                )
                if sent:
                    self.offline_alert_sent = True

    async def heartbeat_loop(self):
        """Hourly proof-of-life log line (first one ~60s after startup)."""
        await asyncio.sleep(60)
        while True:
            if self.sensor_connected:
                wifi = self.wifi_summary()
                logging.info(
                    f"heartbeat: water {'LOW ⚠️' if self.water_is_low else 'OK'}, sensor connected"
                    + (f", {wifi}" if wifi else "")
                )
            else:
                mins = 0
                if self.disconnected_since is not None:
                    mins = int((datetime.now() - self.disconnected_since).total_seconds() // 60)
                logging.info(
                    f"heartbeat: sensor OFFLINE for {mins}m, "
                    f"last known water state {'LOW' if self.water_is_low else 'OK'}"
                )
            await asyncio.sleep(3600)

    async def weekly_summary_loop(self):
        while True:
            await asyncio.sleep(60)
            if not WEEKLY_SUMMARY_ENABLED:
                continue
            now = datetime.now()
            if now.weekday() == WEEKLY_SUMMARY_DAY and now.hour == WEEKLY_SUMMARY_HOUR:
                if self.last_weekly_summary_date != now.date():
                    if await self.send_weekly_summary(now):
                        self.last_weekly_summary_date = now.date()

    async def send_weekly_summary(self, now):
        days_running = (now - self.stats_start_time).days
        hours_running = (now - self.stats_start_time).seconds // 3600

        if not self.sensor_connected:
            sensor_status = "OFFLINE ⚠️"
        elif self.water_is_low:
            sensor_status = "LOW WATER"
        else:
            sensor_status = "OK"

        subject = "📊 Water Monitor: Weekly System Summary"
        message = f"""Hello! This is your weekly check-in from the Water Level Monitor.
The server is UP and RUNNING on the Mac mini.

--- Weekly Stats ---
Monitoring Since: {self.stats_start_time.strftime('%Y-%m-%d %H:%M:%S')} (Uptime: {days_running} days, {hours_running} hours)
Low Water Events Triggered: {self.low_water_events}
Total Alerts Sent: {self.emails_sent}
Current System Status: {sensor_status}
Sensor Connection: {self.wifi_summary() or 'unknown'}

---
System will now reset the weekly counters for the next reporting period.
"""
        success = await self.send_email_notification(subject, message)
        if success:
            logging.info("Weekly summary email sent successfully.")
            self.stats_start_time = now
            self.low_water_events = 0
            self.emails_sent = 0
        else:
            logging.warning("Weekly summary email failed, will retry next cycle.")
        return success

    # --------------------------------------------------------------------- run

    def resolve_host(self):
        try:
            socket.getaddrinfo(SENSOR_HOST, SENSOR_PORT)
            return SENSOR_HOST
        except socket.gaierror:
            logging.warning(f"Cannot resolve {SENSOR_HOST}, using fallback {SENSOR_HOST_FALLBACK}")
            return SENSOR_HOST_FALLBACK

    async def run(self):
        host = self.resolve_host()
        logging.info(f"Water Monitor Server starting — sensor at {host}:{SENSOR_PORT}")

        zc = zeroconf.Zeroconf()
        self.client = APIClient(host, SENSOR_PORT, None, noise_psk=API_ENCRYPTION_KEY)
        self.disconnected_since = datetime.now()  # offline until first connect

        self.reconnect_logic = ReconnectLogic(
            client=self.client,
            on_connect=self.on_connect,
            on_disconnect=self.on_disconnect,
            zeroconf_instance=zc,
            name="water-sensor",
            on_connect_error=self.on_connect_error,
        )
        await self.reconnect_logic.start()

        await asyncio.gather(
            self.watchdog_loop(),
            self.weekly_summary_loop(),
            self.heartbeat_loop(),
        )


def main():
    setup_logging()
    print("=" * 60)
    print("Water Level Monitor Server (ESP32 sensor via ESPHome API)")
    print("=" * 60)
    monitor = WaterMonitorServer()
    try:
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")


if __name__ == "__main__":
    main()
