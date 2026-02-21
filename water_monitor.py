#!/usr/bin/env python3
"""
Water Level Monitor for Raspberry Pi
Monitors water level using a float switch and sends email alerts when water is low
"""

import RPi.GPIO as GPIO
import time
import smtplib
import logging
import os
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logging.handlers import TimedRotatingFileHandler

# Verify working directory before importing config
EXPECTED_DIR = "/home/erictran/Script/water-monitor"
current_dir = os.getcwd()

if not os.path.exists("config.py"):
    print(f"ERROR: config.py not found in current directory: {current_dir}")
    print(f"Expected directory: {EXPECTED_DIR}")
    print(f"Please run from the correct directory or update the systemd service WorkingDirectory")
    sys.exit(1)

if current_dir != EXPECTED_DIR:
    print(f"WARNING: Running from unexpected directory")
    print(f"Current:  {current_dir}")
    print(f"Expected: {EXPECTED_DIR}")
    print(f"Continuing anyway since config.py was found...")

# Import configuration
from config import (
    FLOAT_PIN,
    CHECK_INTERVAL,
    DEBOUNCE_TIME,
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
    ALERT_ON_WATER_RESTORED
)

class WaterLevelMonitor:
    """Monitor water level using float switch and send email alerts"""
    
    def __init__(self):
        """Initialize the water level monitor"""
        self.last_email_time = None
        self.water_is_low = False
        self.low_water_start_time = None
        
        # Setup logging with rotation (daily rotation, keep 5 days)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO if ENABLE_DETAILED_LOGGING else logging.WARNING)
        
        # Clear existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()
            
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler (rotates every midnight, keeps 3 days)
        file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=3)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Stream handler (console)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FLOAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Using pull-up: pin stays HIGH until float switch closes to GND
        
        logging.info("Water Level Monitor initialized")
        logging.info(f"Float switch on GPIO pin {FLOAT_PIN}")
        logging.info(f"Check interval: {CHECK_INTERVAL} seconds")
        logging.info(f"Email notifications: {'Enabled' if EMAIL_NOTIFICATIONS_ENABLED else 'Disabled'}")
    
    def check_water_level(self):
        """
        Check current water level from float switch
        Returns: True if water is OK, False if water is low
        """
        # Read GPIO pin
        pin_state = GPIO.input(FLOAT_PIN)
        
        # With pull-up resistor:
        # HIGH (1) = float switch open = water level LOW
        # LOW (0) = float switch closed to GND = water level OK
        
        water_ok = (pin_state == GPIO.LOW)
        return water_ok
    
    def can_send_email(self):
        """Check if enough time has passed since last email (cooldown period)"""
        if self.last_email_time is None:
            return True
        
        time_since_last_email = datetime.now() - self.last_email_time
        cooldown_period = timedelta(minutes=EMAIL_COOLDOWN_MINUTES)
        
        return time_since_last_email >= cooldown_period
    
    def send_email_notification(self, subject, message):
        """Send email notification"""
        if not EMAIL_NOTIFICATIONS_ENABLED:
            logging.info("Email notifications disabled, skipping email")
            return False
        
        if not EMAIL_FROM or not EMAIL_PASSWORD or not EMAIL_TO:
            logging.warning("Email notifications enabled but credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_FROM
            msg['To'] = ', '.join(EMAIL_TO)
            msg['Subject'] = subject
            
            # Add timestamp to message
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            full_message = f"""
{message}

Timestamp: {current_time}
Location: Raspberry Pi Water Monitor
GPIO Pin: {FLOAT_PIN}

This is an automated alert from your Water Level Monitor.
"""
            
            msg.attach(MIMEText(full_message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            
            # Ensure EMAIL_TO is properly handled as a list
            recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())
            server.quit()
            
            logging.info(f"Email notification sent: {subject}")
            self.last_email_time = datetime.now()
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False
    
    def handle_low_water(self):
        """Handle low water level detection"""
        current_time = datetime.now()
        
        # If this is the first detection, start the debounce timer
        if self.low_water_start_time is None:
            self.low_water_start_time = current_time
            logging.info("Low water level detected, starting debounce timer")
            return
        
        # Check if debounce time has passed
        time_in_low_state = (current_time - self.low_water_start_time).total_seconds()
        
        if time_in_low_state >= DEBOUNCE_TIME:
            # Water has been low for the debounce period
            if not self.water_is_low:
                # This is a new low water event
                self.water_is_low = True
                logging.warning("⚠️  LOW WATER LEVEL CONFIRMED!")
                
                if ALERT_ON_LOW_WATER and self.can_send_email():
                    subject = "⚠️ ALERT: Water Level is LOW"
                    message = """
WARNING: Water level has dropped below the safe threshold!

The float switch has detected low water for more than {debounce} seconds.
Please refill the water container as soon as possible.

Action Required:
- Check water container
- Refill water if needed
- Verify float switch is working properly
""".format(debounce=DEBOUNCE_TIME)
                    
                    self.send_email_notification(subject, message)
                else:
                    logging.info("Email cooldown active or alerts disabled, skipping notification")
    
    def handle_water_restored(self):
        """Handle water level restoration"""
        if self.water_is_low:
            # Water level has been restored
            self.water_is_low = False
            self.low_water_start_time = None
            logging.info("✓ Water level restored to normal")
            
            if ALERT_ON_WATER_RESTORED:
                subject = "✓ Water Level Restored"
                message = """
Good news! The water level has been restored to normal.

The float switch indicates the water container has been refilled.
System is now operating normally.
"""
                self.send_email_notification(subject, message)
        else:
            # Reset debounce timer if water is OK
            self.low_water_start_time = None
    
    def run(self):
        """Main monitoring loop"""
        logging.info("Starting water level monitoring...")
        logging.info("Press Ctrl+C to stop")
        
        try:
            while True:
                water_ok = self.check_water_level()
                
                if water_ok:
                    # Water level is OK
                    if ENABLE_DETAILED_LOGGING:
                        logging.info("Water level OK")
                    self.handle_water_restored()
                else:
                    # Water level is LOW
                    logging.info("Float switch triggered - water level low")
                    self.handle_low_water()
                
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logging.info("\nMonitoring stopped by user")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            GPIO.cleanup()
            logging.info("GPIO cleanup complete")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Water Level Monitor for Raspberry Pi")
    print("=" * 60)
    print(f"Float switch on GPIO pin {FLOAT_PIN} (BCM numbering)")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Debounce time: {DEBOUNCE_TIME} seconds")
    print(f"Email alerts: {'Enabled' if EMAIL_NOTIFICATIONS_ENABLED else 'Disabled'}")
    print("=" * 60)
    print()
    
    monitor = WaterLevelMonitor()
    monitor.run()

if __name__ == "__main__":
    main()
