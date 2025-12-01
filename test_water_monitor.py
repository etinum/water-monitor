#!/usr/bin/env python3
"""
Test script for water level monitor
Tests GPIO reading and email functionality
"""

import RPi.GPIO as GPIO
import time
from config import FLOAT_PIN

def test_float_switch():
    """Test the float switch reading"""
    print("=" * 60)
    print("Water Level Monitor - Float Switch Test")
    print("=" * 60)
    print(f"Testing GPIO pin {FLOAT_PIN} (BCM numbering)")
    print()
    print("Float switch behavior:")
    print("  - HIGH (1) = Water level OK (float is up)")
    print("  - LOW (0) = Water level LOW (float is down)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FLOAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    try:
        while True:
            pin_state = GPIO.input(FLOAT_PIN)
            
            if pin_state == GPIO.HIGH:
                status = "✓ Water level OK (float is UP)"
            else:
                status = "⚠️  Water level LOW (float is DOWN)"
            
            print(f"Pin {FLOAT_PIN}: {pin_state} - {status}")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

if __name__ == "__main__":
    test_float_switch()
