import random
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import time

# Configuration
PAN_PIN = 12  # GPIO pin connected to the pan servo
TILT_PIN = 13  # GPIO pin connected to the tilt servo
SAFE_ANGLE_RANGE = (10, 170)  # Safe angles to avoid over-rotation

# Set up servos with pigpio factory for more precise control
factory = PiGPIOFactory()

servo_pan = AngularServo(
    PAN_PIN,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.42 / 1000,
    max_pulse_width=2.35 / 1000,
    pin_factory=factory,
)

servo_tilt = AngularServo(
    TILT_PIN,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.42 / 1000,
    max_pulse_width=2.35 / 1000,
    pin_factory=factory,
)


def move_servos():
    """
    Move servos to random safe angles for testing.
    """
    pan_angle = random.uniform(*SAFE_ANGLE_RANGE)
    tilt_angle = random.uniform(*SAFE_ANGLE_RANGE)

    print(f"Moving servos to Pan: {pan_angle:.2f}°, Tilt: {tilt_angle:.2f}°")
    servo_pan.angle = pan_angle
    servo_tilt.angle = tilt_angle
    time.sleep(2)  # Hold position for 2 seconds


def main():
    try:
        print("Moving servos to random positions...")
        for _ in range(5):  # Move to 5 random positions
            move_servos()
            time.sleep(1)  # Short pause between movements
        print("Servo test complete.")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        servo_pan.detach()
        servo_tilt.detach()


if __name__ == "__main__":
    main()
