#!/usr/bin/env python3
"""
Test email notifications for water level monitor
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from config import (
    EMAIL_NOTIFICATIONS_ENABLED,
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_FROM,
    EMAIL_PASSWORD,
    EMAIL_TO
)

def test_email():
    """Test email notification system"""
    print("=" * 60)
    print("Water Level Monitor - Email Test")
    print("=" * 60)
    
    if not EMAIL_NOTIFICATIONS_ENABLED:
        print("❌ Email notifications are DISABLED in config.py")
        return False
    
    if not EMAIL_FROM or not EMAIL_PASSWORD or not EMAIL_TO:
        print("❌ Email configuration incomplete in config.py")
        print(f"   EMAIL_FROM: {'✓' if EMAIL_FROM else '❌ Missing'}")
        print(f"   EMAIL_PASSWORD: {'✓' if EMAIL_PASSWORD else '❌ Missing'}")
        print(f"   EMAIL_TO: {'✓' if EMAIL_TO else '❌ Missing'}")
        return False
    
    print(f"SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"From: {EMAIL_FROM}")
    print(f"To: {', '.join(EMAIL_TO)}")
    print()
    print("Sending test email...")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = ', '.join(EMAIL_TO)
        msg['Subject'] = "✓ Water Monitor - Email Test"
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
This is a test email from your Water Level Monitor.

If you receive this email, your email notifications are configured correctly!

Test Details:
- Timestamp: {current_time}
- SMTP Server: {SMTP_SERVER}:{SMTP_PORT}
- From: {EMAIL_FROM}
- To: {', '.join(EMAIL_TO)}

Your water level monitoring system is ready to send alerts.

Next steps:
1. Run test_water_monitor.py to test the float switch
2. Run water_monitor.py to start monitoring
3. Consider setting up as a systemd service for automatic startup
"""
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        
        recipients = EMAIL_TO if isinstance(EMAIL_TO, list) else [EMAIL_TO]
        server.sendmail(EMAIL_FROM, recipients, msg.as_string())
        server.quit()
        
        print("✓ Email sent successfully!")
        print(f"Check your inbox at: {', '.join(EMAIL_TO)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        print()
        print("Common issues:")
        print("1. Gmail App Password not set correctly")
        print("2. 2-Factor Authentication not enabled on Gmail")
        print("3. Network connectivity issues")
        print("4. SMTP server or port incorrect")
        return False

if __name__ == "__main__":
    test_email()
