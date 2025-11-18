#!/bin/bash
# Vino Temperature Control - Installation Script v0.5
# For Raspberry Pi with Raspberry Pi OS

set -e

echo "=================================="
echo "Vino Temperature Control v0.5"
echo "Installation Script"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the actual user who called sudo
ACTUAL_USER=${SUDO_USER:-$USER}
INSTALL_DIR="/home/$ACTUAL_USER/vino_temp_control_v0.5"

echo "Installing for user: $ACTUAL_USER"
echo "Installation directory: $INSTALL_DIR"
echo ""

# Update system
echo "Step 1: Updating system packages..."
apt-get update
echo ""

# Install system dependencies
echo "Step 2: Installing system dependencies..."
apt-get install -y python3 python3-pip python3-venv python3-dev git
echo ""

# Enable 1-Wire interface
echo "Step 3: Configuring 1-Wire interface for DS18B20 sensors..."
if ! grep -q "^dtoverlay=w1-gpio" /boot/firmware/config.txt 2>/dev/null && \
   ! grep -q "^dtoverlay=w1-gpio" /boot/config.txt 2>/dev/null; then
    # Try new location first (Bookworm)
    if [ -f /boot/firmware/config.txt ]; then
        echo "dtoverlay=w1-gpio" >> /boot/firmware/config.txt
        echo "Added w1-gpio overlay to /boot/firmware/config.txt"
    # Fall back to old location
    elif [ -f /boot/config.txt ]; then
        echo "dtoverlay=w1-gpio" >> /boot/config.txt
        echo "Added w1-gpio overlay to /boot/config.txt"
    else
        echo "Warning: Could not find config.txt. Please enable 1-Wire manually."
    fi
else
    echo "1-Wire interface already configured"
fi

# Load 1-Wire modules now (if not loaded)
modprobe w1-gpio 2>/dev/null || true
modprobe w1-therm 2>/dev/null || true
echo ""

# Create installation directory
echo "Step 4: Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy files (assuming script is run from extracted directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    echo "Copying application files..."
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
fi

# Set ownership
chown -R "$ACTUAL_USER":"$ACTUAL_USER" "$INSTALL_DIR"
echo ""

# Install Python dependencies
echo "Step 5: Installing Python dependencies..."
sudo -u "$ACTUAL_USER" pip3 install --break-system-packages Flask RPi.GPIO 2>/dev/null || \
sudo -u "$ACTUAL_USER" pip3 install Flask RPi.GPIO
echo ""

# Create systemd service
echo "Step 6: Creating systemd service..."
cat > /etc/systemd/system/vino-temp-control.service << EOF
[Unit]
Description=Vino Temperature Control System
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload
echo "Systemd service created: vino-temp-control.service"
echo ""

# Ask if user wants to enable and start the service
read -p "Do you want to enable and start the service now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl enable vino-temp-control.service
    systemctl start vino-temp-control.service
    echo "Service enabled and started!"
    echo ""
    echo "Check status with: sudo systemctl status vino-temp-control.service"
else
    echo "Service created but not enabled."
    echo "To enable later: sudo systemctl enable vino-temp-control.service"
    echo "To start later: sudo systemctl start vino-temp-control.service"
fi
echo ""

# Get IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Access the web interface at:"
echo "  http://$IP_ADDR:5000"
echo ""
echo "Or manually start the application:"
echo "  cd $INSTALL_DIR"
echo "  python3 app.py"
echo ""
echo "For troubleshooting, see INSTALL.md"
echo ""
echo "NOTE: A reboot is recommended to ensure 1-Wire interface is fully active."
read -p "Do you want to reboot now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Rebooting in 5 seconds..."
    sleep 5
    reboot
fi
