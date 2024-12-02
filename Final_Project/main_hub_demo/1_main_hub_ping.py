import time
import pigpio

# GPIO pin setup
SPEAKER_PIN = 18  # GPIO pin connected to the speaker

# Constants
PING_FREQUENCY = 1000  # 1 kHz ping signal
PING_DURATION = 0.1  # Duration of the ping in seconds
PING_INTERVAL = 2  # Time between pings in seconds

# Initialize pigpio
pi = pigpio.pi()  # Connect to the local Pi's GPIO daemon


def emit_ping(frequency=PING_FREQUENCY, duration=PING_DURATION):
    """
    Emit a 1 kHz ping signal using pigpio for accurate frequency.
    """
    print(f"Emitting {frequency} Hz ping signal for {duration} seconds...")
    pi.set_PWM_frequency(SPEAKER_PIN, frequency)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 128)  # 50% duty cycle (range 0-255)
    time.sleep(duration)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 0)  # Turn off the signal
    print("Ping signal complete.")


def main():
    print("Main hub initialized. Generating periodic pings.")
    try:
        while True:
            emit_ping()
            time.sleep(PING_INTERVAL)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        pi.stop()  # Cleanup GPIO


if __name__ == "__main__":
    main()
