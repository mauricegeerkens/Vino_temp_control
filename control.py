# Basic control logic for heating/cooling
# GPIO relay control for Raspberry Pi 4

# Try to import RPi.GPIO, fallback to mock if not available
try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)  # Disable GPIO warnings
except (ImportError, RuntimeError):
    class MockGPIO:
        BCM = OUT = HIGH = LOW = None
        def setmode(self, *a, **kw): pass
        def setup(self, *a, **kw): pass
        def output(self, *a, **kw): pass
        def cleanup(self): pass
        def setwarnings(self, *a, **kw): pass
    GPIO = MockGPIO()
import atexit

TARGET_TEMP = 12.0  # Example target temperature in Celsius
DEFAULT_DEVIATION = 0.5  # Default deadband in Celsius
HEAT_PIN = 17  # GPIO 17 (physical pin 11)
COOL_PIN = 27  # GPIO 27 (physical pin 13)

GPIO.setmode(GPIO.BCM)
GPIO.setup(HEAT_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(COOL_PIN, GPIO.OUT, initial=GPIO.LOW)

def cleanup_gpio():
    GPIO.output(HEAT_PIN, GPIO.LOW)
    GPIO.output(COOL_PIN, GPIO.LOW)
    GPIO.cleanup()
atexit.register(cleanup_gpio)


class TempController:
    def __init__(self, target=TARGET_TEMP, deviation=DEFAULT_DEVIATION, safety_sensor_name=None, safety_off=28.0, safety_on=25.0):
        self.target = target
        self.deviation = deviation
        self.safety_sensor_name = safety_sensor_name
        self.safety_off = safety_off
        self.safety_on = safety_on
        self.heating_blocked = False
        self.cooling_blocked = False  # Frost protection flag
        self.min_temp = None  # Minimum temperature from all sensors for frost protection
        self.current_state = 'idle'  # Track actual state: 'idle', 'heating', 'cooling'
        self.is_heating = False  # Actual GPIO state
        self.is_cooling = False  # Actual GPIO state

    def should_heat(self, current_temp, safety_temp=None):
        # Safety logic: block heating if safety sensor is above threshold
        if safety_temp is not None:
            if safety_temp >= self.safety_off:
                self.heating_blocked = True
            elif safety_temp <= self.safety_on:
                self.heating_blocked = False
        if self.heating_blocked:
            return False
        return current_temp is not None and current_temp < self.target - self.deviation

    def check_frost_protection(self, all_temps):
        """Frost protection: block cooling if any sensor is at/below 0°C, unblock when all above 5°C"""
        if not all_temps:
            self.min_temp = None
            return
        
        # Get minimum temperature from all sensors
        valid_temps = [t for t in all_temps if t is not None]
        if not valid_temps:
            self.min_temp = None
            return
        
        min_temp = min(valid_temps)
        self.min_temp = min_temp  # Store for status reporting
        
        # Block cooling if any sensor at or below 0°C
        if min_temp <= 0.0:
            if not self.cooling_blocked:
                print(f"⚠️ FROST PROTECTION ACTIVATED: Min temp {min_temp}°C <= 0°C - Cooling blocked until all sensors reach 5°C")
            self.cooling_blocked = True
        # Unblock cooling only when all sensors above 5°C (hysteresis)
        elif min_temp >= 5.0:
            if self.cooling_blocked:
                print(f"✓ FROST PROTECTION DEACTIVATED: Min temp {min_temp}°C >= 5°C - Cooling unblocked")
            self.cooling_blocked = False
        # Between 0-5°C: maintain current state (hysteresis)
        elif self.cooling_blocked:
            print(f"⚠️ FROST PROTECTION ACTIVE: Min temp {min_temp}°C - Waiting for 5°C to re-enable cooling")

    def should_cool(self, current_temp):
        # Check frost protection first
        if self.cooling_blocked:
            return False
        return current_temp is not None and current_temp > self.target + self.deviation

    def update_relays(self, current_temp, safety_temp=None, all_temps=None):
        # Check frost protection with all sensor temperatures
        if all_temps:
            self.check_frost_protection(all_temps)
        
        # Only one system active at a time, with safety sensor
        should_heat = self.should_heat(current_temp, safety_temp)
        should_cool = self.should_cool(current_temp)
        
        # Determine desired state
        if should_heat:
            desired_state = 'heating'
        elif should_cool:
            desired_state = 'cooling'
        else:
            desired_state = 'idle'
        
        # Only update GPIOs if state changes
        if desired_state != self.current_state:
            print(f"State change: {self.current_state} -> {desired_state} (temp={current_temp}, target={self.target}, dev={self.deviation}, safety={safety_temp}, heating_blocked={self.heating_blocked}, cooling_blocked={self.cooling_blocked})")
            
            if desired_state == 'heating':
                GPIO.output(HEAT_PIN, GPIO.HIGH)
                GPIO.output(COOL_PIN, GPIO.LOW)
                self.is_heating = True
                self.is_cooling = False
                print(f"HEATING ON (GPIO {HEAT_PIN} = HIGH)")
            elif desired_state == 'cooling':
                GPIO.output(HEAT_PIN, GPIO.LOW)
                GPIO.output(COOL_PIN, GPIO.HIGH)
                self.is_heating = False
                self.is_cooling = True
                print(f"COOLING ON (GPIO {COOL_PIN} = HIGH)")
            else:  # idle
                GPIO.output(HEAT_PIN, GPIO.LOW)
                GPIO.output(COOL_PIN, GPIO.LOW)
                self.is_heating = False
                self.is_cooling = False
                print(f"IDLE - Both relays OFF")
            
            self.current_state = desired_state
