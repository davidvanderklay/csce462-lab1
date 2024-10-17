from gpiozero import Servo
import math
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()
factory2 = PiGPIOFactory()

servo = Servo(12, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory)
servo2 = Servo(13, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory2)

def angle(degrees, degrees2):
    servo2.value = math.sin(math.radians(degrees))
    servo.value = math.sin(math.radians(degrees2))

while True:
    key = input('Angle for first motor: ')
    key2 = input('Angle for second motor: ')
    if key == 'q': exit()
    if key2 == 'q': exit()
    else:
        angle(float(key), float(key2))