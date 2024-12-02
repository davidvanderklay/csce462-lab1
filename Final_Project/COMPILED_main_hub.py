import time
import math
import random
import pigpio
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# GPIO pin setup
SPEAKER_PIN = 18  # Output pin connected to the speaker
MIC_PINS = [5, 6, 19]  # Input pins connected to the microphones

# Servo setup
factory = PiGPIOFactory()
factory2 = PiGPIOFactory()
factory3 = PiGPIOFactory()

servo = Servo(
    12, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory
)
servo2 = Servo(
    13, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory2
)
servo3 = Servo(
    26, min_pulse_width=0.42 / 1000, max_pulse_width=2.35 / 1000, pin_factory=factory3
)

# Constants
SPEED_OF_SOUND = 343.0  # Speed of sound in m/s
MIC_DISTANCE = 0.1  # Distance between the center and each microphone in meters
TIMEOUT = 1.0  # Timeout for signal detection in seconds

# Define microphone positions in radians (e.g., 0, 120, and 240 degrees)
MIC_ANGLES = [0, 2 * math.pi / 3, 4 * math.pi / 3]

# Variables
mic_times = [None, None, None]
start_time = None

# Initialize pigpio
pi = pigpio.pi()  # Connect to local Pi's GPIO daemon


def init_gpio():
    for pin in MIC_PINS:
        pi.set_mode(pin, pigpio.INPUT)
        pi.set_pull_up_down(pin, pigpio.PUD_DOWN)
        pi.callback(pin, pigpio.RISING_EDGE, mic_callback)


def cleanup_gpio():
    pi.stop()


def randomMovement():
    twoMotors = random.randint(-90, 90)
    servo.value = math.sin(math.radians(random.randint(-90, 90)))
    servo2.value = math.sin(math.radians(twoMotors))
    servo3.value = math.sin(math.radians(twoMotors))


def mic_callback(pin, level, tick):
    global mic_times
    if level == 1:  # Rising edge detected
        idx = MIC_PINS.index(pin)
        if mic_times[idx] is None:
            mic_times[idx] = time.time()
            print(
                f"Microphone {idx+1} detected signal at {mic_times[idx] - start_time:.6f} seconds"
            )


def emit_beep(frequency=15000, duration=0.1):
    """
    Emit a beep using pigpio for accurate frequency.
    """
    pi.set_PWM_frequency(SPEAKER_PIN, frequency)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 128)  # 50% duty cycle (0-255 range)
    time.sleep(duration)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 0)  # Turn off


def calculate_distance():
    valid_times = [t for t in mic_times if t is not None]
    distances = [(t - start_time) * SPEED_OF_SOUND for t in valid_times]
    estimated_distance = sum(distances) / len(distances) if distances else 0
    print(
        f"Estimated average distance to sound source: {estimated_distance:.2f} meters"
    )
    return estimated_distance


def calculate_position():
    time_diffs = [t - start_time for t in mic_times]
    print(f"Time differences: {time_diffs}")

    dist_diffs = [td * SPEED_OF_SOUND for td in time_diffs]
    print(f"Distance differences: {dist_diffs}")

    x = sum(d * math.cos(angle) for d, angle in zip(dist_diffs, MIC_ANGLES))
    y = sum(d * math.sin(angle) for d, angle in zip(dist_diffs, MIC_ANGLES))

    calculated_angle = math.degrees(math.atan2(y, x))
    calculated_angle = (
        calculated_angle if calculated_angle >= 0 else calculated_angle + 360
    )
    print(f"Calculated angle: {calculated_angle:.2f} degrees")
    estimated_distance = calculate_distance()

    randomMovement()


def main():
    global start_time, mic_times
    init_gpio()
    try:
        while True:
            mic_times = [None, None, None]
            print("Emitting beep...")
            start_time = time.time()
            emit_beep()
            timeout_time = start_time + TIMEOUT
            while None in mic_times and time.time() < timeout_time:
                time.sleep(0.01)
            if None in mic_times:
                print("Timeout: Not all microphones detected the signal.")
            else:
                calculate_position()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        cleanup_gpio()


if __name__ == "__main__":
    main()
