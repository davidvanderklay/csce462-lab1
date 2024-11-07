import RPi.GPIO as GPIO
import time

# Configuration
SPEAKER_PIN = 18  # GPIO pin connected to the speaker
FREQUENCY = 1000  # Frequency of the sound in Hz (15 kHz)
DURATION = 2  # Duration of sound emission in seconds


def emit_beep(frequency=FREQUENCY, duration=DURATION):
    """
    Emit a sound at the specified frequency and duration using PWM.
    """
    pwm = GPIO.PWM(SPEAKER_PIN, frequency)
    pwm.start(50)  # 50% duty cycle
    print(f"Emitting {frequency} Hz sound for {duration} seconds.")
    time.sleep(duration)
    pwm.stop()
    print("Sound emission complete.")


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)

    try:
        emit_beep()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
