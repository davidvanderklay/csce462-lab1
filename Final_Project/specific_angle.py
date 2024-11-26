from gpiozero import Servo
import math
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

# Use a single PiGPIOFactory instance
factory = PiGPIOFactory()

# Initialize servos
servo1 = Servo(12, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory)
servo2 = Servo(13, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory)

def set_angle(degrees1, degrees2):
    # Map angles to servo values
    servo1.value = math.sin(math.radians(degrees1))
    servo2.value = math.sin(math.radians(degrees2))

while True:
    try:
        key1 = input('Angle for first motor (q to quit): ')
        if key1.lower() == 'q':
            break
        key2 = input('Angle for second motor (q to quit): ')
        if key2.lower() == 'q':
            break

        # Convert inputs to float and set servo angles
        set_angle(float(key1), float(key2))
    except ValueError:
        print("Please enter valid numeric angles or 'q' to quit.")
