from gpiozero import Servo
import math
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()
factory2 = PiGPIOFactory()

servo = Servo(12, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory)
servo2 = Servo(13, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory2)

while True:
    for i in range(0, 360):
        servo.value = math.sin(math.radians(i))
        servo2.value = math.sin(math.radians(i))
        sleep(0.01)