import glob
import os
import json
import csv
import time

# Calibration offsets for each sensor (sensor_id: offset)
OFFSET_FILE = 'sensor_offsets.json'

# Memory caches to avoid disk I/O on every sensor read
_offsets_cache = None
_last_log_time = 0  # Track last temperature log time
LOG_INTERVAL = 60  # Only log temperature data every 60 seconds

def load_offsets():
    global _offsets_cache
    if _offsets_cache is None:
        try:
            with open(OFFSET_FILE, 'r') as f:
                _offsets_cache = json.load(f)
        except Exception:
            _offsets_cache = {}
    return _offsets_cache

def save_offsets(offsets):
    global _offsets_cache
    with open(OFFSET_FILE, 'w') as f:
        json.dump(offsets, f)
    _offsets_cache = offsets  # Update cache

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
                    # Apply offset if available (cached in memory)
                    offsets = load_offsets()
                    temp_c += offsets.get(sensor_id, 0.0)
                    return temp_c
    except Exception as e:
        print(f"Error reading sensor {sensor_id}: {e}")
    return None

def read_sensors_by_id(sensor_ids):
    """Read specific sensors by ID - fast, direct lookup"""
    try:
        base_dir = '/sys/bus/w1/devices/'
        
        # Check if we're on a Raspberry Pi with actual sensors
        if not os.path.exists(base_dir):
            # Return mock data for development/testing
            import random
            result = []
            for sensor_id in sensor_ids:
                if sensor_id == '28-mock001':
                    result.append({
                        'id': sensor_id,
                        'temperature': round(12.0 + random.uniform(-0.5, 0.5), 1)
                    })
                elif sensor_id == '28-mock002':
                    result.append({
                        'id': sensor_id,
                        'temperature': round(20.0 + random.uniform(-1.0, 1.0), 1)
                    })
            return result
        
        sensors = []
        for sensor_id in sensor_ids:
            temp = read_single_sensor(sensor_id, base_dir)
            if temp is not None:
                sensors.append({
                    'id': sensor_id,
                    'temperature': temp
                })
        
        return sensors
    except Exception as e:
        print(f"Error in read_sensors_by_id: {e}")
        import traceback
        traceback.print_exc()
        return []

def read_sensors():
    """Read all sensors - returns list with sensor IDs and temperatures"""
    try:
        base_dir = '/sys/bus/w1/devices/'
        
        # Check if we're on a Raspberry Pi with actual sensors
        if not os.path.exists(base_dir):
            # Return mock data for development/testing
            import random
            sensors = [
                {'id': '28-mock001', 'temperature': round(12.0 + random.uniform(-0.5, 0.5), 1)},
                {'id': '28-mock002', 'temperature': round(20.0 + random.uniform(-1.0, 1.0), 1)},
            ]
            return sensors
        
        device_folders = glob.glob(base_dir + '28-*')
        offsets = load_offsets()
        sensors = []
        
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
                            sensors.append({
                                'id': sensor_id,
                                'temperature': temp_c
                            })
            except Exception as e:
                print(f"Error reading sensor {sensor_id}: {e}")
        
        # Log readings for histogram - only every LOG_INTERVAL seconds
        global _last_log_time
        current_time = time.time()
        if current_time - _last_log_time >= LOG_INTERVAL:
            try:
                log_temperature_data(sensors)
                _last_log_time = current_time
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
                sensor.get('temperature', '')
            ])

def get_offsets():
    return load_offsets()

def set_offset(sensor_id, offset):
    offsets = load_offsets()
    offsets[sensor_id] = offset
    save_offsets(offsets)

if __name__ == "__main__":
    print(read_sensors())
