import time
import math
import random
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# Servo setup
factory = PiGPIOFactory()
servo1 = Servo(
    12, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory
)
servo2 = Servo(
    13, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory
)
servo3 = Servo(
    26, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory
)

# Constants
SPEED_OF_SOUND = 343.0  # Speed of sound in m/s
MIC_ANGLES = [0, 2 * math.pi / 3, 4 * math.pi / 3]  # 0, 120, and 240 degrees


def generate_mock_times():
    """
    Simulates response times for microphones.
    """
    base_time = random.uniform(0, 0.01)  # Base time for first mic
    offsets = [
        random.uniform(0, 0.005) for _ in range(2)
    ]  # Simulated offsets for other mics
    return [base_time, base_time + offsets[0], base_time + offsets[1]]


def calculate_position(mic_times):
    """
    Calculate angle and distances based on simulated mic times.
    """
    # Calculate time differences relative to the first mic
    time_diffs = [t - mic_times[0] for t in mic_times]
    print(f"Simulated time differences: {time_diffs}")

    # Calculate distance differences
    dist_diffs = [td * SPEED_OF_SOUND for td in time_diffs]
    print(f"Simulated distance differences: {dist_diffs}")

    # Calculate x, y coordinates for trilateration
    x = sum(d * math.cos(angle) for d, angle in zip(dist_diffs, MIC_ANGLES))
    y = sum(d * math.sin(angle) for d, angle in zip(dist_diffs, MIC_ANGLES))

    # Determine angle and normalize
    calculated_angle = math.degrees(math.atan2(y, x))
    calculated_angle = (
        calculated_angle if calculated_angle >= 0 else calculated_angle + 360
    )
    print(f"Calculated angle: {calculated_angle:.2f} degrees")

    return calculated_angle


def move_servos(angle):
    """
    Move servos based on the calculated angle.
    - Servo1 (base) adjusts to point towards the angle.
    - Servo2 and Servo3 simulate vertical adjustments.
    """
    # Normalize angle to servo range (-90 to 90 degrees)
    servo1_position = math.sin(math.radians(angle))
    servo2_position = math.sin(math.radians(angle / 2))
    servo3_position = math.cos(math.radians(angle / 2))

    print(
        f"Moving servo1 to {servo1_position:.2f}, servo2 to {servo2_position:.2f}, servo3 to {servo3_position:.2f}"
    )

    servo1.value = servo1_position
    servo2.value = servo2_position
    servo3.value = servo3_position


def main():
    print("Starting demo...")
    try:
        while True:
            # Generate mock microphone times
            mic_times = generate_mock_times()
            print(f"Simulated microphone times: {mic_times}")

            # Calculate position based on mock times
            angle = calculate_position(mic_times)

            # Move servos to represent pointing towards the calculated angle
            move_servos(angle)

            # Pause before next cycle
            time.sleep(2)
    except KeyboardInterrupt:
        print("Demo interrupted by user.")


if __name__ == "__main__":
    main()
