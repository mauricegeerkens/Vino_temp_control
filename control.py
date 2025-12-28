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

    def should_cool(self, current_temp):
        return current_temp is not None and current_temp > self.target + self.deviation

    def update_relays(self, current_temp, safety_temp=None):
        # Only one system active at a time, with safety sensor
        should_heat = self.should_heat(current_temp, safety_temp)
        should_cool = self.should_cool(current_temp)
        
        # Debug logging
        print(f"Control: temp={current_temp}, target={self.target}, dev={self.deviation}, heat={should_heat}, cool={should_cool}, safety={safety_temp}, blocked={self.heating_blocked}")
        
        if should_heat:
            GPIO.output(HEAT_PIN, GPIO.HIGH)
            GPIO.output(COOL_PIN, GPIO.LOW)
            print(f"HEATING ON (GPIO {HEAT_PIN} = HIGH)")
        elif should_cool:
            GPIO.output(HEAT_PIN, GPIO.LOW)
            GPIO.output(COOL_PIN, GPIO.HIGH)
            print(f"COOLING ON (GPIO {COOL_PIN} = HIGH)")
        else:
            GPIO.output(HEAT_PIN, GPIO.LOW)
            GPIO.output(COOL_PIN, GPIO.LOW)
