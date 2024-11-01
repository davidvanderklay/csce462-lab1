import RPi.GPIO as GPIO
import time
import math
import random
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import threading

# -------------------- Configuration --------------------

# GPIO pin setup
SPEAKER_PIN = 18  # Output pin connected to the speaker
MIC_PINS = [5, 6, 19]  # Input pins connected to the microphones

# Servo setup
factory = PiGPIOFactory()

servo_pan = AngularServo(
    12,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.42 / 1000,
    max_pulse_width=2.35 / 1000,
    pin_factory=factory,
)

servo_tilt = AngularServo(
    13,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.42 / 1000,
    max_pulse_width=2.35 / 1000,
    pin_factory=factory,
)

# Constants
FREQUENCY = 15000  # 15 kHz
BEEP_DURATION = 0.1  # Duration of beep in seconds
COOLDOWN_TIME = 1.0  # Cooldown period in seconds
SAFE_ANGLE_RANGE = (10, 170)  # Safe angles to prevent servo over-rotation

# Variables
last_detection_time = 0
detection_lock = threading.Lock()

# -------------------- GPIO Setup --------------------


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)
    GPIO.setup(MIC_PINS, GPIO.IN)
    for pin in MIC_PINS:
        GPIO.add_event_detect(pin, GPIO.RISING, callback=mic_callback, bouncetime=200)


def cleanup_gpio():
    GPIO.cleanup()


# -------------------- Frequency Generation --------------------


def emit_beep(frequency=FREQUENCY, duration=BEEP_DURATION):
    """
    Emits a beep at the specified frequency and duration using PWM.
    """
    pwm = GPIO.PWM(SPEAKER_PIN, frequency)
    pwm.start(50)  # 50% duty cycle
    time.sleep(duration)
    pwm.stop()


# -------------------- Frequency Detection --------------------


def mic_callback(channel):
    """
    Callback function triggered when a microphone detects the frequency.
    Initiates the homing process if cooldown has passed.
    """
    global last_detection_time
    with detection_lock:
        current_time = time.time()
        if current_time - last_detection_time > COOLDOWN_TIME:
            last_detection_time = current_time
            print(
                f"Frequency detected on MIC_PIN {channel}. Initiating homing process."
            )
            homing_process()


# -------------------- Homing Process --------------------


def homing_process():
    """
    Moves the servos to random safe angles.
    """
    # Generate random angles within the safe range
    pan_angle = random.uniform(*SAFE_ANGLE_RANGE)
    tilt_angle = random.uniform(*SAFE_ANGLE_RANGE)

    print(f"Moving servos to Pan: {pan_angle:.2f}°, Tilt: {tilt_angle:.2f}°")

    # Move servos to the random angles
    servo_pan.angle = pan_angle
    servo_tilt.angle = tilt_angle


# -------------------- Demo Function --------------------


def demo():
    """
    Main demo loop:
    - Emits a 15 kHz beep.
    - Waits for a cooldown period before emitting the next beep.
    """
    try:
        while True:
            print("Emitting 15 kHz beep...")
            emit_beep()
            # Wait for the beep duration plus a small buffer
            time.sleep(BEEP_DURATION + 0.05)
            # Cooldown to allow for detection and homing process
            time.sleep(COOLDOWN_TIME)
    except KeyboardInterrupt:
        print("\nDemo terminated by user.")
    finally:
        cleanup_gpio()


# -------------------- Main Execution --------------------

if __name__ == "__main__":
    init_gpio()
    print("Demo started. Press Ctrl+C to exit.")
    demo()
