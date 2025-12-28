import glob
import os
import json
import csv
import time

import json

import os
# Calibration offsets for each sensor (sensor_id: offset)
OFFSET_FILE = 'sensor_offsets.json'
NAME_FILE = 'sensor_names.json'

def load_offsets():
    try:
        with open(OFFSET_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_offsets(offsets):
    with open(OFFSET_FILE, 'w') as f:
        json.dump(offsets, f)

def load_names():
    try:
        with open(NAME_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_names(names):
    with open(NAME_FILE, 'w') as f:
        json.dump(names, f)

def read_single_sensor(sensor_id, base_dir='/sys/bus/w1/devices/'):
    """Read a single sensor by ID for fast critical reads"""
    try:
        folder = os.path.join(base_dir, sensor_id)
        if not os.path.exists(folder):
            return None
            
        with open(folder + '/w1_slave', 'r') as f:
            lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_c = float(lines[1][equals_pos+2:]) / 1000.0
                    # Apply offset if available
                    offsets = load_offsets()
                    temp_c += offsets.get(sensor_id, 0.0)
                    return temp_c
    except Exception as e:
        print(f"Error reading sensor {sensor_id}: {e}")
    return None

def read_sensors_by_name(sensor_names):
    """Read specific sensors by name (e.g., ['Room', 'SafetySensor']) - faster than reading all"""
    try:
        base_dir = '/sys/bus/w1/devices/'
        
        # Check if we're on a Raspberry Pi with actual sensors
        if not os.path.exists(base_dir):
            # Return mock data for development/testing
            import random
            result = []
            names_db = load_names()
            for mock_id, mock_name in [('28-mock001', 'Room'), ('28-mock002', 'SafetySensor')]:
                if mock_name in sensor_names:
                    result.append({
                        'id': mock_id,
                        'name': mock_name,
                        'temperature': round(12.0 + random.uniform(-0.5, 0.5), 1) if mock_name == 'Room' else round(20.0 + random.uniform(-1.0, 1.0), 1)
                    })
            return result
        
        # Find which sensor IDs correspond to the requested names
        names_db = load_names()
        name_to_id = {name: sid for sid, name in names_db.items() if name in sensor_names}
        
        sensors = []
        for name, sensor_id in name_to_id.items():
            temp = read_single_sensor(sensor_id, base_dir)
            if temp is not None:
                sensors.append({
                    'id': sensor_id,
                    'name': name,
                    'temperature': temp
                })
        
        return sensors
    except Exception as e:
        print(f"Error in read_sensors_by_name: {e}")
        import traceback
        traceback.print_exc()
        return []

def read_sensors():
    """Read all sensors - use sparingly, prefer read_sensors_by_name for specific sensors"""
    try:
        base_dir = '/sys/bus/w1/devices/'
        
        # Check if we're on a Raspberry Pi with actual sensors
        if not os.path.exists(base_dir):
            # Return mock data for development/testing
            import random
            names = load_names()
            sensors = [
                {'id': '28-mock001', 'name': names.get('28-mock001', 'Room'), 'temperature': round(12.0 + random.uniform(-0.5, 0.5), 1)},
                {'id': '28-mock002', 'name': names.get('28-mock002', 'SafetySensor'), 'temperature': round(20.0 + random.uniform(-1.0, 1.0), 1)},
            ]
            return sensors
        
        device_folders = glob.glob(base_dir + '28-*')
        offsets = load_offsets()
        temps = {}
        for folder in device_folders:
            sensor_id = os.path.basename(folder)
            try:
                with open(folder + '/w1_slave', 'r') as f:
                    lines = f.readlines()
                    if lines[0].strip()[-3:] == 'YES':
                        equals_pos = lines[1].find('t=')
                        if equals_pos != -1:
                            temp_c = float(lines[1][equals_pos+2:]) / 1000.0
                            # Apply offset if available
                            temp_c += offsets.get(sensor_id, 0.0)
                            temps[sensor_id] = temp_c
            except Exception as e:
                print(f"Error reading sensor {sensor_id}: {e}")
                temps[sensor_id] = None
        
        # Build sensors list with names
        names = load_names()
        sensors = []
        for sensor_id, temp in temps.items():
            sensors.append({
                'id': sensor_id,
                'name': names.get(sensor_id, ''),
                'temperature': temp
            })
        
        # Log readings for histogram
        try:
            log_temperature_data(sensors)
        except Exception as e:
            print(f"Error logging temperature data: {e}")
        
        return sensors
    except Exception as e:
        print(f"Critical error in read_sensors: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list on critical error
        return []

def log_temperature_data(sensors):
    log_file = 'temperature_log.csv'
    timestamp = int(time.time())
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        for sensor in sensors:
            writer.writerow([
                timestamp,
                sensor.get('id', ''),
                sensor.get('name', ''),
                sensor.get('temperature', '')
            ])

def get_offsets():
    return load_offsets()

def set_offset(sensor_id, offset):
    offsets = load_offsets()
    offsets[sensor_id] = offset
    save_offsets(offsets)

def get_names():
    return load_names()

def set_name(sensor_id, name):
    names = load_names()
    names[sensor_id] = name
    save_names(names)

if __name__ == "__main__":
    print(read_sensors())
