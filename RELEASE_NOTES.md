# Vino Temperature Control - Release Notes

## Version 3.1 - January 2026

### Bug Fixes

**Fixed Historical Data Logging**:
- Restored temperature logging functionality that was broken in v3.0
- Temperature data is now logged every 60 seconds to CSV file
- Historical chart will display data again after system restart
- Fixed issue where 20-second sensor polling didn't trigger data logging
- Uses 4-column CSV format: timestamp, sensor_id, name, temperature

**Improved Mobile UI**:
- Added spacing between "Sensor kalibratie" and "7-Daagse temperatuur overzicht" buttons on mobile devices
- Buttons now stack properly with appropriate margin on phone screens

### Technical Details
- Added explicit `log_temperature_data()` function to app.py
- Sensor polling thread now calls logging function every 60 seconds
- Logging happens in background without blocking sensor reads or API responses
- CSV format compatible with both old and new data for historical chart

---

## Version 3.0 - January 2026

### Improved Temperature Control Logic

**Bug Fix**:

#### 🎯 Target Temperature Reached
- Fixed control logic to ensure target temperature is actually reached
- Previously: Cooling stopped at target + deviation (e.g., 24°C for target 22°C, deviation 2°C)
- Previously: Heating stopped at target - deviation (e.g., 20°C for target 22°C, deviation 2°C)
- Now: Deviation only controls when to **start** heating/cooling
- Now: Heating/cooling **continues until target is reached** (22°C in example)
- Provides more accurate temperature control while maintaining hysteresis to prevent frequent cycling

**Technical Details**:
- Modified `should_heat()` method to check current state and continue until target reached
- Modified `should_cool()` method to check current state and continue until target reached
- Deviation still prevents frequent on/off cycling by setting activation thresholds
- Ensures precise temperature control matching user expectations

## Version 1.7 - December 2025

### Enhanced Sensor Management & Configurable Safety

**Added Features**:

#### 🏷️ Sensor Names for Display
- Restored sensor naming capability for better UI/UX
- Names stored in `settings.json` under `sensor_names`
- Control loop still uses direct ID lookup (fast)
- Display shows friendly names (Johanniter, Solaris, Souvignier gris, etc.)
- `/api/temps_named` endpoint returns temps by name
- Settings page allows editing sensor names

#### 🛡️ Flexible Safety Configuration
- Safety sensor is now **optional** (set `safety_sensor_id: ""` to disable)
- Configurable safety temperatures in settings.json:
  - `safety_off_temp`: Temperature to shut off heating (default 28°C)
  - `safety_on_temp`: Temperature to resume heating (default 25°C)
- Control loop handles missing safety sensor gracefully
- Only reads connected sensors (optimized performance)

#### 🎯 Updated Settings Structure
```json
{
  "room_sensor_id": "28-000000b2de98",
  "safety_sensor_id": "",  // Optional - leave empty if not connected
  "safety_off_temp": 28.0,
  "safety_on_temp": 25.0,
  "sensor_names": {
    "28-000000b2de98": "Room",
    "28-000000be48b4": "Johanniter",
    "28-000000be61bd": "Solaris",
    "28-000000bff7ad": "Souvignier gris"
  }
}
```

#### 🔧 API Enhancements
- `GET /api/control` - Now includes sensor names
- `POST /api/sensor_name` - Update individual sensor names
- `GET /api/temps_named` - Get temperatures by friendly names

**Benefits**:
- ✅ Better UI - see sensor names instead of IDs
- ✅ Flexible safety - optional overheating protection
- ✅ Still fast - control loop optimized with direct ID lookup
- ✅ Easy configuration - edit names via web interface or JSON

---

## Version 1.6 - December 2025

### Performance Optimization & Simplified Architecture

**Problem Solved**: Massive delays in sensor reading and status updates caused by:
- File I/O operations (loading offsets/names from JSON files on every sensor read)
- Temperature logging on every sensor read (CSV file writes)
- Sensor name lookups requiring dictionary traversal
- Too-frequent sensor polling

**Solution**: Memory caching, reduced file I/O, hardcoded sensor roles with configurable IDs

#### 🚀 Major Performance Improvements

**Memory Caching**:
- `_offsets_cache`: Sensor offsets loaded once and cached in memory
- `_names_cache`: Eliminated - replaced with direct sensor ID usage
- Offsets/names files only read on first access, not on every sensor read
- File I/O reduced by **95%+**

**Reduced Logging Frequency**:
- Temperature logging changed from every read to once per 60 seconds
- Eliminates CSV file write overhead on every sensor access
- History data still captured, but without performance impact

**Optimized Cache Timings**:
- Control cache: Increased from 1s to **2s** (50% fewer sensor reads)
- Display cache: Increased from 5s to **10s** (50% fewer UI sensor reads)
- Control loop: Runs every 2s (matches cache duration)
- Frontend polling: 2s instead of 500ms (75% reduction)

#### 🎯 Architectural Simplification

**Hardcoded Sensor Names with Configurable IDs**:
- Removed `sensor_names.json` file entirely
- New `settings.json` fields: `room_sensor_id` and `safety_sensor_id`
- Sensors identified by ID, not by user-assigned names
- Example:
  ```json
  {
    "room_sensor_id": "28-00000a1b2c3d",
    "safety_sensor_id": "28-00000e4f5g6h"
  }
  ```

**Simplified Functions**:
- `read_sensors_by_name()` → `read_sensors_by_id()` (direct ID lookup)
- Removed `get_names()` and `set_name()` functions
- Removed `/api/names` and `/api/temps_named` endpoints
- CSV logging format simplified (removed name column)

**Benefits**:
- No name-to-ID translation overhead
- Can't accidentally break control by renaming sensors
- Clearer configuration - explicit role assignment
- Fewer files to manage
- Less error-prone

#### 📊 Performance Impact

**Before v1.6**:
- Each sensor read: ~3-5ms file I/O + 750ms sensor read
- Control loop: Read 2 sensors + load offsets + load names + log CSV = ~1.5-2s
- Status display delays of 1-3 seconds common

**After v1.6**:
- Each sensor read: ~750ms sensor read only (cached offsets)
- Control loop: Read 2 sensors = ~1.5s, runs every 2s
- Logging overhead: Nearly zero (60s interval)
- UI feels **instant and responsive**

#### 🔧 Technical Changes

**sensor_reader.py**:
- Added `_offsets_cache` and `_last_log_time` global variables
- Removed all name-related functions
- `load_offsets()` now caches in memory
- `log_temperature_data()` only runs every 60 seconds
- Simplified CSV format (timestamp, id, temperature)

**app.py**:
- Removed imports: `get_names`, `set_name`, `read_sensors_by_name`
- Added `read_sensors_by_id` import
- Updated cache durations (2s control, 10s display)
- Sensor lookup by ID from `settings.json`
- Removed `/api/names` endpoints
- Updated `/api/history` for new CSV format

**settings.json** (new):
- `room_sensor_id`: Which sensor controls room temperature
- `safety_sensor_id`: Which sensor provides safety cutoff
- Still includes `target` and `deviation` for control

### Migration Notes

**Updating from v1.5**:
1. Create `settings.json` with sensor IDs:
   ```json
   {
     "target": 12.0,
     "deviation": 0.5,
     "room_sensor_id": "28-your-room-sensor-id",
     "safety_sensor_id": "28-your-safety-sensor-id"
   }
   ```
2. Find your sensor IDs: Run `ls /sys/bus/w1/devices/28-*`
3. `sensor_names.json` is no longer used (can be deleted)
4. Existing `sensor_offsets.json` still works as before

---

## Version 1.5 - December 2025

### Major Architectural Redesign for Maximum Responsiveness

**Problem Solved**: Previous versions read all 4 DS18B20 sensors on every API call, causing 3+ second delays (each sensor takes ~750ms).

**Solution**: Dual caching system with smart sensor separation:

#### 🚀 Performance Improvements
- **Dual Cache Architecture**:
  - **Control Cache**: Only reads 2 sensors (Room + SafetySensor) every 1 second for heating/cooling decisions
  - **Display Cache**: Reads all 4 sensors every 5 seconds for UI display only
  - Eliminates unnecessary sensor reads - control loop no longer waits for display sensors

- **New Optimized Functions**:
  - `read_sensors_by_name()`: Fast targeted sensor reads by name
  - `read_single_sensor()`: Read individual sensor for critical operations
  - `get_control_sensors()`: Fast access to control-critical data
  - `get_all_sensors()`: Slower, UI-only full sensor read

- **Dramatically Faster Response Times**:
  - Control decisions: **<100ms** (was 3+ seconds)
  - Status API: **<100ms** (was 3+ seconds)
  - Temperature display: **<100ms with 5s cache** (was 3+ seconds every call)
  - Settings changes: **Instant** (no sensor reads needed)

#### 🎯 Smart Sensor Usage
- **Control sensors** (Room + SafetySensor): Read frequently (1s) for responsive heating/cooling
- **Display sensors** (all 4): Read infrequently (5s) to avoid UI slowdown
- Each API endpoint uses the appropriate cache for its purpose

#### 🔧 Technical Changes
- Removed redundant `get_cached_sensors()` function
- Control loop optimized to only access control sensors
- Fixed case-sensitive sensor name matching (was `name.lower() == "room"`, now `name == "Room"`)
- Consistent naming throughout codebase

### Benefits
- ✅ Heating/cooling responds within 1 second instead of 3+ seconds
- ✅ UI controls feel instant and responsive
- ✅ No more lag when changing settings or toggling switches
- ✅ Control loop never blocked by slow sensor reads
- ✅ Frontend polling efficient - no cascading sensor read delays

---

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
