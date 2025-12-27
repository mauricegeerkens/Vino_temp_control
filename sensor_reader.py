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

def read_sensors():
    base_dir = '/sys/bus/w1/devices/'
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
    log_temperature_data(sensors)
    return sensors

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
