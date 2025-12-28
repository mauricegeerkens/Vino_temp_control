# Vino Temperature Control - Release Notes

## Version 1.3 - December 2025

### Major Performance Improvements
- **Ultra-Fast Sensor Data Caching**: 
  - Implemented 0.5-second cache for sensor readings
  - All API endpoints now use cached data for instant responses
  - Eliminates redundant sensor reads across multiple simultaneous requests

- **Watchdog System for Freeze Prevention**:
  - New `/api/watchdog` endpoint monitors backend health
  - Tracks last sensor access timestamp
  - Frontend automatically detects and warns when system becomes unresponsive
  - Visual warning banner appears after 3 consecutive watchdog failures

- **Drastically Improved Update Rates**:
  - Frontend polling increased from 2s to **500ms** (4x faster)
  - Control loop update interval reduced from 5s to **1s** (5x faster)
  - Near-instant UI responsiveness for all controls

### Enhanced Reliability
- **Request Timeout Protection**:
  - 3-second timeouts on all standard API requests
  - 5-second timeout for large history data requests
  - Prevents hanging/freezing when backend is slow or unresponsive

- **Comprehensive Error Handling**:
  - All fetch requests include error catching and logging
  - User-friendly error messages when operations fail
  - Graceful degradation instead of complete UI freeze

### Technical Details
- Sensor cache with thread-safe locking mechanism
- Watchdog timestamp updates on every sensor access
- Health monitoring considers system unhealthy after 10s of inactivity
- Frontend freeze detection triggers warning after 3 failed watchdog checks

### Bug Fixes
- Fixed potential race conditions in concurrent sensor reads
- Improved stability under high request load
- Better handling of network timeouts

## Version 1.0 - December 2025

### Major Features
- **Light State Persistence**: Light on/off state now persists across page reloads and app restarts
  - Added `light_state.json` for state storage
  - GPIO pin initialized to saved state on startup
  - New GET endpoint `/api/light` to query current light state

- **Control Enable Persistence**: Temperature control enable/disable state properly persists
  - State synced with UI on page load
  - No more state flickering when navigating between pages

- **Improved State Management**: Complete overhaul of UI state synchronization
  - Both "Regeling" and "Licht" switches now load their saved state immediately
  - UI always reflects actual server state
  - Smooth transitions with no visual flickering

### Bug Fixes
- **Fixed target temperature update delay**: Target temperature now updates immediately when pressing "Opslaan"
  - Previously took ~50 seconds due to periodic refresh overwriting the value
  - Form submission now immediately updates display with server response
  
- **Fixed switch state on navigation**: Switches maintain correct state when navigating between pages
  - Removed conditional state sync that prevented proper initialization
  - UI now always syncs with server state on every refresh

### Improvements
- Enhanced error handling for switch toggles
- Cleaner code with dedicated UI update functions (`updateControlUI()`, `updateLightUI()`)
- Better state consistency across all pages
- More reliable GPIO state management

## Version 0.9 - December 2025

### Bug Fixes
- **Fixed application slowness**: Increased dashboard update interval from 3 seconds to 5 seconds for better performance
- **Fixed target temperature saving**: Temperature settings now properly persist when clicking "Opslaan" button
  - Added dirty flag system to prevent automatic overwrite of user input
  - Input fields are now protected from auto-update while being edited
- **Fixed unresponsive buttons**: "Regeling aan/uit" and "Licht aan/uit" buttons now properly respond to clicks
  - Added missing glass-box CSS styling to control panels

### Improvements
- Reduced server load with less frequent dashboard updates
- Better user experience when editing temperature settings
- More responsive and visible control buttons

## Version 0.8.1 - December 2025

### Features
- **Named Sensor Mapping**: Sensors are now assigned to display positions by name instead of random discovery order
- **Persistent Sensor Assignment**: Once named, sensors always appear in the correct position on the dashboard
- **New API Endpoint**: Added `/api/temps_named` to retrieve temperatures organized by sensor name

### Breaking Changes
- **Sensor naming required**: Users must assign names to sensors via the Settings page:
  - "Room" for klimaat kast (main room temperature)
  - "Johanniter" for Johanniter barrel
  - "Solaris" for Solaris barrel
  - "Souvignier gris" for Souvignier gris barrel

### Technical Changes
- Modified `index.html` to use name-based sensor lookup instead of array index
- Added `/api/temps_named` endpoint in `app.py` for name-based temperature retrieval

### Migration Guide
1. Update to version 0.8.1
2. Go to Settings page (Sensor kalibratie)
3. Assign exact names to each sensor as listed above
4. Names are case-sensitive and must match exactly

## Version 0.7 - November 2025

### Changes
- **Light relay GPIO updated**: Changed from GPIO 22 (pin 15) to GPIO 23 (pin 16)
- **Documentation updates**: All pin assignments updated to reflect GPIO 23
- **Verified working configuration**: Confirmed with physical relay module setup

### GPIO Assignments
- **GPIO 4 (Pin 7)**: DS18B20 1-Wire data bus
- **GPIO 17 (Pin 11)**: Heating relay control
- **GPIO 27 (Pin 13)**: Cooling relay control
- **GPIO 23 (Pin 16)**: Light relay control ⬅️ UPDATED

### Installation
See `INSTALL.md` for detailed installation instructions.

Quick install:
```bash
unzip vino_temp_control_v0.7.zip
cd vino_temp_control_v0.7
sudo ./install.sh
```

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
