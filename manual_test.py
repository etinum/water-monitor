#!/usr/bin/env python3
"""
Manual test script - Send test email on demand
Useful for testing email configuration without waiting for low water
"""

import sys
from water_monitor import WaterLevelMonitor

def main():
    print("=" * 60)
    print("Water Level Monitor - Manual Email Test")
    print("=" * 60)
    print()
    print("This will send a test email immediately.")
    print()
    
    # Ask for confirmation
    response = input("Send test email? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Test cancelled.")
        return
    
    print()
    print("Initializing monitor...")
    monitor = WaterLevelMonitor()
    
    print("Sending test email...")
    subject = "🧪 Water Monitor - Manual Test"
    message = """
This is a MANUAL TEST email from your Water Level Monitor.

You triggered this test email manually using manual_test.py.

If you receive this email, your water monitor is correctly configured
and ready to send automatic alerts when water levels are low.

Test successful! ✓
"""
    
    success = monitor.send_email_notification(subject, message)
    
    if success:
        print()
        print("✓ Test email sent successfully!")
        print(f"Check your inbox at: {', '.join(monitor.EMAIL_TO) if hasattr(monitor, 'EMAIL_TO') else 'configured addresses'}")
    else:
        print()
        print("❌ Failed to send test email.")
        print("Check the error messages above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
