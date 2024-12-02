import time
import pigpio

# GPIO pin setup
SPEAKER_PIN = 18  # GPIO pin connected to the speaker

# Constants
RESPONSE_FREQUENCY = 15000  # 15 kHz response signal
RESPONSE_DURATION = 0.1  # Duration of the response in seconds

# Initialize pigpio
pi = pigpio.pi()  # Connect to the local Pi's GPIO daemon


def emit_response_signal(frequency=RESPONSE_FREQUENCY, duration=RESPONSE_DURATION):
    """
    Emit a 15 kHz response signal using pigpio for accurate frequency.
    """
    print(f"Emitting {frequency} Hz response signal for {duration} seconds...")
    pi.set_PWM_frequency(SPEAKER_PIN, frequency)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 128)  # 50% duty cycle (range 0-255)
    time.sleep(duration)
    pi.set_PWM_dutycycle(SPEAKER_PIN, 0)  # Turn off the signal
    print("Response signal complete.")


def main():
    print("Receiver ready. Press Enter to emit response signal, or Ctrl+C to exit.")
    try:
        while True:
            input("Press Enter to simulate receiving a ping and emit response...")
            emit_response_signal()
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        pi.stop()  # Cleanup GPIO


if __name__ == "__main__":
    main()
