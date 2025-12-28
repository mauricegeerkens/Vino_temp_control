# --- Imports ---
import csv
import time
import json
import subprocess
import atexit
import threading
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from sensor_reader import read_sensors, read_sensors_by_id, get_offsets, set_offset
from control import TempController

# --- Dual Sensor Cache System ---
# Control cache: Only Room + SafetySensor, read frequently for fast control
control_cache = {'data': None, 'timestamp': None, 'lock': threading.Lock()}
CONTROL_CACHE_DURATION = 2.0  # Increased from 1s to 2s - reduces I/O by 50%

# Display cache: All sensors for UI, read less frequently to avoid slowdown
display_cache = {'data': None, 'timestamp': None, 'lock': threading.Lock()}
DISPLAY_CACHE_DURATION = 10.0  # Increased from 5s to 10s - reduces UI load

watchdog_timestamp = time.time()  # Global watchdog timestamp

def get_control_sensors():
    """Get Room + SafetySensor only - fast, for control loop"""
    global watchdog_timestamp
    watchdog_timestamp = time.time()
    
    with control_cache['lock']:
        now = time.time()
        if (control_cache['data'] is None or 
            control_cache['timestamp'] is None or 
            (now - control_cache['timestamp']) > CONTROL_CACHE_DURATION):
            # Read only the 2 sensors needed for control using IDs from settings
            room_id = settings.get('room_sensor_id', '28-mock001')
            safety_id = settings.get('safety_sensor_id', '28-mock002')
            control_cache['data'] = read_sensors_by_id([room_id, safety_id])
            control_cache['timestamp'] = now
        return control_cache['data']

def get_all_sensors():
    """Get all sensors - slower, for UI display only"""
    global watchdog_timestamp
    watchdog_timestamp = time.time()
    
    with display_cache['lock']:
        now = time.time()
        if (display_cache['data'] is None or 
            display_cache['timestamp'] is None or 
            (now - display_cache['timestamp']) > DISPLAY_CACHE_DURATION):
            # Read all sensors for display
            display_cache['data'] = read_sensors()
            display_cache['timestamp'] = now
        return display_cache['data']

# --- GPIO Setup ---
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)  # Disable warnings about channels in use
except (ImportError, RuntimeError):
    class MockGPIO:
        BCM = OUT = HIGH = LOW = None
        def setmode(self, *a, **kw): pass
        def setup(self, *a, **kw): pass
        def output(self, *a, **kw): pass
        def cleanup(self): pass
        def setwarnings(self, *a, **kw): pass
    GPIO = MockGPIO()

# GPIO Pin Configuration
LIGHT_PIN = 23  # GPIO 23 (physical pin 16)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT, initial=GPIO.LOW)  # Explicit initial state
print(f"GPIO {LIGHT_PIN} (pin 16) initialized to LOW (OFF)")

# Cleanup GPIO on exit
def cleanup_light_gpio():
    try:
        GPIO.output(LIGHT_PIN, GPIO.LOW)  # Turn off
        print(f"GPIO {LIGHT_PIN} cleaned up")
    except:
        pass
    GPIO.cleanup()

atexit.register(cleanup_light_gpio)

# --- App Setup ---
app = Flask(__name__)

# --- Control Enable Persistence ---
CONTROL_ENABLE_FILE = "control_enable.json"

def load_control_enabled():
    try:
        with open(CONTROL_ENABLE_FILE, "r") as f:
            return json.load(f).get("enabled", True)
    except Exception:
        return True

def save_control_enabled(enabled):
    with open(CONTROL_ENABLE_FILE, "w") as f:
        json.dump({"enabled": enabled}, f)

control_enabled = load_control_enabled()

# --- Light State Persistence ---
LIGHT_STATE_FILE = "light_state.json"

def load_light_state():
    try:
        with open(LIGHT_STATE_FILE, "r") as f:
            return json.load(f).get("on", False)
    except Exception:
        return False

def save_light_state(on):
    with open(LIGHT_STATE_FILE, "w") as f:
        json.dump({"on": on}, f)

light_on = load_light_state()
# Initialize GPIO with saved state
GPIO.output(LIGHT_PIN, GPIO.HIGH if light_on else GPIO.LOW)
print(f"Light restored to state: {'ON' if light_on else 'OFF'}")

# --- Settings Persistence ---
SETTINGS_FILE = "settings.json"

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()
target = settings.get("target", 12.0)
deviation = settings.get("deviation", 0.5)
SAFETY_SENSOR_NAME = "SafetySensor"  # Change this to your safety sensor's name
controller = TempController(target=target, deviation=deviation, safety_sensor_name=SAFETY_SENSOR_NAME, safety_off=28.0, safety_on=25.0)

# --- Control Loop ---
def control_loop():
    """Background thread that controls heating/cooling relays"""
    print("Control loop started")
    while True:
        try:
            if control_enabled:
                # Only read the 2 sensors needed for control - fast!
                sensors = get_control_sensors()
                room_temp = None
                safety_temp = None
                
                # Get sensor IDs from settings
                room_id = settings.get('room_sensor_id', '28-mock001')
                safety_id = settings.get('safety_sensor_id', '28-mock002')
                
                for sensor in sensors:
                    sensor_id = sensor.get('id', '')
                    temp = sensor.get('temperature', None)
                    if sensor_id == room_id:
                        room_temp = temp
                    elif sensor_id == safety_id:
                        safety_temp = temp
                
                # Update the relays based on current temperature
                controller.update_relays(room_temp, safety_temp)
            else:
                # If control is disabled, turn off both relays and reset state
                from control import GPIO, HEAT_PIN, COOL_PIN
                if controller.current_state != 'idle':
                    GPIO.output(HEAT_PIN, GPIO.LOW)
                    GPIO.output(COOL_PIN, GPIO.LOW)
                    controller.is_heating = False
                    controller.is_cooling = False
                    controller.current_state = 'idle'
                    print("Control disabled - relays OFF, state reset to idle")
        except Exception as e:
            print(f"Error in control loop: {e}")
        
        time.sleep(2)  # Check every 2 seconds (matches control cache duration)

# Start control loop in background thread
control_thread = threading.Thread(target=control_loop, daemon=True)
control_thread.start()

# --- API Endpoints ---
@app.route('/api/watchdog', methods=['GET'])
def api_watchdog():
    """Watchdog endpoint to check if backend is responsive"""
    global watchdog_timestamp
    current_time = time.time()
    time_since_update = current_time - watchdog_timestamp
    is_healthy = time_since_update < 15  # Considered unhealthy if no updates for 15 seconds (increased for slow sensor reads)
    return jsonify({
        'healthy': is_healthy,
        'last_update': watchdog_timestamp,
        'time_since_update': time_since_update,
        'timestamp': current_time
    }), 200

@app.route('/api/light', methods=['POST'])
def api_light():
    global light_on
    data = request.json
    on = data.get('on', False)
    light_on = bool(on)
    print(f"Light API called: on={light_on}, setting GPIO to {'HIGH' if light_on else 'LOW'}")
    # Direct logic for active-HIGH relay modules
    GPIO.output(LIGHT_PIN, GPIO.HIGH if light_on else GPIO.LOW)
    save_light_state(light_on)
    print(f"GPIO {LIGHT_PIN} set successfully")
    return jsonify({'on': light_on}), 200

@app.route('/api/light', methods=['GET'])
def api_get_light():
    return jsonify({'on': light_on}), 200

@app.route('/api/shutdown', methods=['POST'])
def api_shutdown():
    subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
    return jsonify({'status': 'shutting down'}), 200

@app.route('/api/control_enable', methods=['POST'])
def api_control_enable():
    global control_enabled
    data = request.json
    enabled = data.get('enabled', True)
    control_enabled = bool(enabled)
    save_control_enabled(control_enabled)
    return jsonify({'enabled': control_enabled}), 200

@app.route('/api/offsets', methods=['GET'])
def api_get_offsets():
    try:
        return jsonify(get_offsets())
    except Exception as e:
        print(f"Error in /api/offsets GET: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({}), 200  # Return empty dict instead of failing

@app.route('/api/offsets', methods=['POST'])
def api_set_offset():
    data = request.json
    sensor_id = data.get('sensor_id')
    offset = data.get('offset')
    if sensor_id is not None and offset is not None:
        set_offset(sensor_id, float(offset))
        return jsonify({'sensor_id': sensor_id, 'offset': float(offset)}), 200
    return jsonify({'error': 'Missing sensor_id or offset'}), 400

@app.route('/api/temps')
def get_temps():
    try:
        # Use display cache - all sensors, updated every 10 seconds
        sensors = get_all_sensors()
        # Convert list to dictionary for backwards compatibility
        temps = {}
        for sensor in sensors:
            temps[sensor['id']] = sensor['temperature']
        return jsonify(temps)
    except Exception as e:
        print(f"Error in /api/temps: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/control', methods=['POST'])
def set_control():
    data = request.json
    target = data.get('target')
    deviation = data.get('deviation')
    changed = False
    if target is not None:
        try:
            controller.target = float(target)
            settings["target"] = controller.target
            changed = True
        except (TypeError, ValueError):
            pass
    if deviation is not None:
        try:
            dev_val = float(deviation)
            controller.deviation = dev_val
            settings["deviation"] = dev_val
            changed = True
        except (TypeError, ValueError):
            pass
    if changed:
        save_settings(settings)
    return jsonify({'target': controller.target, 'deviation': controller.deviation}), 200

@app.route('/api/status')
def get_status():
    try:
        # Use control cache - only Room + SafetySensor, updated every 2 seconds
        sensors = get_control_sensors()
        room_temp = None
        safety_temp = None
        
        # Get sensor IDs from settings
        room_id = settings.get('room_sensor_id', '28-mock001')
        safety_id = settings.get('safety_sensor_id', '28-mock002')
        
        for sensor in sensors:
            sensor_id = sensor.get('id', '')
            temp = sensor.get('temperature', None)
            if sensor_id == room_id:
                room_temp = temp
            elif sensor_id == safety_id:
                safety_temp = temp
        
        # Return ACTUAL controller state, not recalculated values
        status = {
            'should_heat': controller.is_heating if control_enabled else False,
            'should_cool': controller.is_cooling if control_enabled else False,
            'current_state': controller.current_state if control_enabled else 'idle',
            'target': controller.target,
            'deviation': controller.deviation,
            'room_temp': room_temp,
            'safety_temp': safety_temp,
            'heating_blocked': controller.heating_blocked,
            'control_enabled': control_enabled,
            'light_on': light_on
        }
        return jsonify(status)
    except Exception as e:
        print(f"Error in /api/status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- Page Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/history')
def api_history():
    log_file = 'temperature_log.csv'
    data = []
    try:
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                ts = int(row[0])
                data.append({
                    'timestamp': ts,
                    'id': row[1],
                    'temperature': float(row[2]) if row[2] else None
                })
    except FileNotFoundError:
        pass
    return jsonify(data)

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

if __name__ == "__main__":
    # Allow port to be configured via environment variable for development
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
