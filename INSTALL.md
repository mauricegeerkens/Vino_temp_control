# Vino Temperature Control - Installation Guide v0.5

## Quick Installation for Raspberry Pi

This guide will help you install and configure the Vino Temperature Control system on your Raspberry Pi.

## Prerequisites

- Raspberry Pi (tested on Pi 4) with Raspberry Pi OS (Bookworm or later)
- Internet connection for initial setup
- DS18B20 temperature sensors properly wired (see README.md for wiring details)
- Relay modules for heating/cooling/light control (optional)

## Installation Steps

### 1. Extract the Release Package

```bash
cd ~
unzip vino_temp_control_v0.5.zip
cd vino_temp_control_v0.5
```

### 2. Run the Installation Script

The installation script will:
- Install system dependencies
- Enable 1-Wire interface for temperature sensors
- Create a Python virtual environment
- Install Python dependencies
- Configure the systemd service (optional)

```bash
sudo chmod +x install.sh
sudo ./install.sh
```

Follow the prompts during installation.

### 3. Manual Start (Testing)

To test the application without the service:

```bash
cd ~/vino_temp_control_v0.5
python3 app.py
```

Access the web interface at: `http://<your-pi-ip>:5000`

### 4. Enable Auto-Start (Recommended)

If you chose to install the systemd service during installation:

```bash
sudo systemctl enable vino-temp-control.service
sudo systemctl start vino-temp-control.service
```

Check status:
```bash
sudo systemctl status vino-temp-control.service
```

View logs:
```bash
sudo journalctl -u vino-temp-control.service -f
```

## Post-Installation Configuration

1. **Access the Web Interface**: Open a browser to `http://<raspberry-pi-ip>:5000`
2. **Configure Sensors**: Go to Settings page to:
   - Assign friendly names to your sensors (e.g., "Wine Room", "Barrel 1")
   - Set calibration offsets if needed
3. **Set Temperature Control**: On the main page:
   - Set your target temperature
   - Configure deadband (hysteresis)
   - Enable/disable control relays

## Troubleshooting

### Temperature Sensors Not Detected

1. Check 1-Wire is enabled:
```bash
sudo raspi-config
# Interface Options -> 1-Wire -> Enable
```

2. Reboot:
```bash
sudo reboot
```

3. Verify sensors are detected:
```bash
ls /sys/bus/w1/devices/
```
You should see directories like `28-xxxxxxxxxxxx` for each sensor.

### Service Won't Start

Check logs for errors:
```bash
sudo journalctl -u vino-temp-control.service -n 50
```

### Permission Issues

Ensure the application directory has correct permissions:
```bash
sudo chown -R $USER:$USER ~/vino_temp_control_v0.5
```

## Updating

To update to a newer version:

1. Stop the service if running:
```bash
sudo systemctl stop vino-temp-control.service
```

2. Backup your data:
```bash
cp ~/vino_temp_control_v0.5/temperature_log.csv ~/temperature_log.csv.backup
cp ~/vino_temp_control_v0.5/control_enable.json ~/control_enable.json.backup
```

3. Extract new version and copy data back

4. Restart the service:
```bash
sudo systemctl start vino-temp-control.service
```

## Uninstallation

To remove the application:

```bash
sudo systemctl stop vino-temp-control.service
sudo systemctl disable vino-temp-control.service
sudo rm /etc/systemd/system/vino-temp-control.service
sudo systemctl daemon-reload
rm -rf ~/vino_temp_control_v0.5
```

## Support

For issues and questions, please visit:
https://github.com/mauricegeerkens/Vino_temp_control
