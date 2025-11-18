# Vino Temperature Control - Release Notes

## Version 0.6 - November 2025

### Bug Fixes
- Fixed GPIO warnings on startup
- Improved light relay control with better debugging
- Fixed GPIO initialization conflicts between app.py and control.py
- Added explicit initial GPIO states for reliability
- Enhanced error handling in GPIO cleanup

### Improvements
- Added console logging for light button debugging
- Better GPIO setup with `initial` parameter
- Disabled GPIO warnings to reduce console noise

## Version 0.5 - November 2025

### Features
- **Web-based Dashboard**: Real-time temperature monitoring with Bootstrap UI
- **Multi-Sensor Support**: Monitor wine room + up to 3 barrel sensors (DS18B20)
- **Automated Temperature Control**: PID-style control with heating/cooling relays
- **Historical Charting**: View temperature trends over time with Chart.js
- **Sensor Configuration**: 
  - Custom friendly names for each sensor
  - Calibration offsets for accuracy
- **Light Control**: Manual light switch control via GPIO
- **Offline Operation**: Works without internet connection once installed
- **Data Logging**: CSV-based temperature logging for historical analysis
- **Auto-Start Service**: systemd integration for automatic startup on boot

### Hardware Requirements
- Raspberry Pi (tested on Pi 4)
- DS18B20 digital temperature sensors (1-4 sensors)
- 4.7kΩ pull-up resistor for 1-Wire bus
- Relay modules (optional, for heating/cooling/light control)

### GPIO Assignments
- **GPIO 4 (Pin 7)**: DS18B20 1-Wire data bus
- **GPIO 17 (Pin 11)**: Heating relay control
- **GPIO 27 (Pin 13)**: Cooling relay control
- **GPIO 22 (Pin 15)**: Light relay control

### Installation
See `INSTALL.md` for detailed installation instructions.

Quick install:
```bash
unzip vino_temp_control_v0.5.zip
cd vino_temp_control_v0.5
sudo ./install.sh
```

### Files Included
- `app.py` - Main Flask application
- `control.py` - Temperature control logic
- `sensor_reader.py` - DS18B20 sensor interface
- `requirements.txt` - Python dependencies
- `install.sh` - Automated installation script
- `vino-temp-control.service` - systemd service file
- `static/` - Web assets (CSS, JS, images)
- `templates/` - HTML templates
- `README.md` - Project documentation
- `INSTALL.md` - Installation guide
- `VERSION` - Version identifier

### Configuration
- Default port: 5000
- Target temperature: Configurable via web UI
- Deadband: Configurable via web UI
- Control enable/disable: Persisted in `control_enable.json`
- Temperature history: Logged in `temperature_log.csv`

### Known Issues
- First temperature reading after startup may take 10-15 seconds
- Raspberry Pi OS Bookworm changed config.txt location (handled by installer)

### Support
GitHub: https://github.com/mauricegeerkens/Vino_temp_control

### License
See repository for license information.
