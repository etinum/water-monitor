#!/bin/bash
# Setup script for Water Level Monitor

echo "=========================================="
echo "Water Level Monitor - Setup Script"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Some features may not work correctly"
    echo ""
fi

# Install Python GPIO library
echo "Installing Python GPIO library..."
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio

# Create log directory if it doesn't exist
echo "Creating log directory..."
mkdir -p /home/erictran/Script
chmod 755 /home/erictran/Script

# Make scripts executable
echo "Making scripts executable..."
chmod +x water_monitor.py
chmod +x test_water_monitor.py
chmod +x test_email.py

# Test email configuration
echo ""
echo "=========================================="
echo "Testing email configuration..."
echo "=========================================="
python3 test_email.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test the float switch: python3 test_water_monitor.py"
echo "2. Run the monitor: python3 water_monitor.py"
echo "3. Install as service: sudo cp water-monitor.service /etc/systemd/system/"
echo "                       sudo systemctl enable water-monitor.service"
echo "                       sudo systemctl start water-monitor.service"
echo ""
