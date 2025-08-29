# Vino_temp_control

## Overview
A temperature control and monitoring system for a wine room and up to 3 external barrels, built on Raspberry Pi 4 with Python (Flask) backend and a Bootstrap-based web frontend. Supports sensor calibration, friendly naming, relay control, historical charting, and offline usage.

## Hardware Wiring
### DS18B20 Temperature Sensors
- Data line: **GPIO 4** (Pin 7)
- Power: 3.3V (Pin 1)
- Ground: GND (Pin 6)
- Pull-up resistor: 4.7kΩ between Data and 3.3V
- Connect multiple sensors in parallel on the data line.

### Relay Control (Heating/Cooling)
- **Heating Relay:** GPIO 17 (Pin 11)
- **Cooling Relay:** GPIO 27 (Pin 13)
- Relays should be 5V modules suitable for Pi GPIO control.
- Connect relay IN to GPIO, VCC to 5V (Pin 2/4), GND to GND (Pin 6/9/14).

### Example Wiring Table
| Function         | GPIO | Pin | Description         |
|------------------|------|-----|---------------------|
| DS18B20 Data     | 4    | 7   | 1-Wire Data         |
| Heating Relay    | 17   | 11  | Relay IN (Heating)  |
| Cooling Relay    | 27   | 13  | Relay IN (Cooling)  |

## Software Setup
1. Install Python 3.12+ and pip.
2. Clone this repo:
	```bash
	git clone https://github.com/mauricegeerkens/Vino_temp_control.git
	cd Vino_temp_control
	```
3. Install dependencies:
	```bash
	pip install flask
	# For Raspberry Pi only:
	pip install RPi.GPIO
	```
4. Run the app:
	```bash
	python3 app.py
	```

## Usage
- Access the dashboard at `http://<raspberrypi_ip>:5000` on your Pi touchscreen or browser.
- Set target temperature, deadband, and control relays from the dashboard.
- Calibrate sensors and assign friendly names in the Settings page.
- View 7-day temperature history in the History page.

## Offline Usage
- All required static assets (Bootstrap, Chart.js, date adapter) are served locally from `/static/`.
- No internet connection required after initial setup.

## File Structure
- `app.py`: Flask backend and API endpoints
- `sensor_reader.py`: Sensor reading, calibration, naming, logging
- `control.py`: Deadband logic, relay control
- `templates/`: HTML pages (dashboard, settings, history)
- `static/`: Local JS/CSS/images for offline use
- `temperature_log.csv`: Historical temperature data

## Notes
- On non-Raspberry Pi systems, GPIO is mocked for development.
- For real hardware, ensure RPi.GPIO is installed and run on Raspberry Pi OS.
- For questions or wiring help, see comments in `control.py` and `sensor_reader.py`.
- The settings page includes a "Shutdown" button for graceful power-off of the Raspberry Pi. No GPIO or hardware changes are required; it uses the `sudo shutdown -h now` command. You may need to configure `sudo` permissions to allow shutdown without a password for the web server user.