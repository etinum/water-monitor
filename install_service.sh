#!/bin/bash
# Helper script to install water-monitor service with correct paths

echo "=========================================="
echo "Water Monitor - Service Installation"
echo "=========================================="
echo ""

# Get current directory
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

echo "Detected settings:"
echo "  User: $CURRENT_USER"
echo "  Directory: $CURRENT_DIR"
echo ""

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "❌ ERROR: config.py not found in current directory"
    echo "   Please run this script from the water-monitor directory"
    exit 1
fi

# Check if water_monitor.py exists
if [ ! -f "water_monitor.py" ]; then
    echo "❌ ERROR: water_monitor.py not found in current directory"
    echo "   Please run this script from the water-monitor directory"
    exit 1
fi

# Ask for confirmation
echo "This will create a systemd service with these settings:"
echo "  User: $CURRENT_USER"
echo "  WorkingDirectory: $CURRENT_DIR"
echo "  ExecStart: /usr/bin/python3 $CURRENT_DIR/water_monitor.py"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

# Create service file with correct paths
SERVICE_FILE="/tmp/water-monitor.service"

cat > $SERVICE_FILE << EOF
[Unit]
Description=Water Level Monitor
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/water_monitor.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created at $SERVICE_FILE"
echo ""

# Copy to systemd directory
echo "Installing service (requires sudo)..."
sudo cp $SERVICE_FILE /etc/systemd/system/water-monitor.service

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy service file"
    exit 1
fi

echo "✓ Service file installed"
echo ""

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "Enabling service..."
sudo systemctl enable water-monitor.service

# Start service
echo "Starting service..."
sudo systemctl start water-monitor.service

# Check status
echo ""
echo "=========================================="
echo "Service Status:"
echo "=========================================="
sudo systemctl status water-monitor.service --no-pager

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  sudo systemctl status water-monitor.service"
echo "  sudo systemctl stop water-monitor.service"
echo "  sudo systemctl restart water-monitor.service"
echo "  sudo journalctl -u water-monitor.service -f"
echo ""
