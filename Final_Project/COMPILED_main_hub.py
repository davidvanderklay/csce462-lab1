import RPi.GPIO as GPIO
import time
import math
import random
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# GPIO pin setup
SPEAKER_PIN = 18  # Output pin connected to the speaker
MIC_PINS = [5, 6, 19]  # Input pins connected to the microphones

# Servo setup
factory = PiGPIOFactory()
factory2 = PiGPIOFactory()
factory3 = PiGPIOFactory()

servo = Servo(12, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory)
servo2 = Servo(13, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory2)
servo3 = Servo(26, min_pulse_width=0.42/1000, max_pulse_width=2.35/1000, pin_factory=factory3)

# Constants
SPEED_OF_SOUND = 343.0  # Speed of sound in m/s
MIC_DISTANCE = 0.1  # Distance between microphones in meters
TIMEOUT = 1.0  # Timeout for signal detection in seconds

# Variables
mic_times = [None, None, None]
start_time = None


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)
    for pin in MIC_PINS:
        GPIO.setup(pin, GPIO.IN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=mic_callback)


def cleanup_gpio():
    GPIO.cleanup()

def randomMovement():
    twoMotors = random.randint(-90, 90)
    servo.value = math.sin(math.radians(random.randint(-90, 90)))
    servo2.value = math.sin(math.radians(twoMotors))
    servo3.value = math.sin(math.radians(twoMotors))

def mic_callback(channel):
    global mic_times
    idx = MIC_PINS.index(channel)
    if mic_times[idx] is None:
        mic_times[idx] = time.time()
        print(
            f"Microphone {idx+1} detected signal at {mic_times[idx] - start_time:.6f} seconds"
        )


def emit_beep(frequency=15000, duration=0.1):
    pwm = GPIO.PWM(SPEAKER_PIN, frequency)
    pwm.start(50)  # 50% duty cycle
    time.sleep(duration)
    pwm.stop()


def calculate_position():
    time_diffs = [t - start_time for t in mic_times]
    print(f"Time differences: {time_diffs}")

    # Calculate distance differences
    dist_diffs = [td * SPEED_OF_SOUND for td in time_diffs]
    print(f"Distance differences: {dist_diffs}")

    # Simple calculation assuming linear microphone placement
    angle = math.degrees(math.acos((dist_diffs[1] - dist_diffs[0]) / MIC_DISTANCE))
    print(f"Calculated angle: {angle} degrees")

    # Move servos to point towards the object
    # servo_pan.angle = angle
    # servo_tilt.angle = 90  # Assuming horizontal movement only for simplicity
    randomMovement()


def main():
    global start_time, mic_times
    init_gpio()
    try:
        while True:
            # Reset times
            mic_times = [None, None, None]
            print("Emitting beep...")
            start_time = time.time()
            emit_beep()
            # Wait for signals or timeout
            timeout_time = start_time + TIMEOUT
            while None in mic_times and time.time() < timeout_time:
                time.sleep(0.01)
            if None in mic_times:
                print("Timeout: Not all microphones detected the signal.")
            else:
                calculate_position()
            time.sleep(1)  # Wait before next cycle
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        cleanup_gpio()


if __name__ == "__main__":
    main()
