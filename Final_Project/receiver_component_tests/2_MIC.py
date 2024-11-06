import RPi.GPIO as GPIO
import time

# Configuration
MIC_PIN = 5  # GPIO pin connected to the microphone
DETECTION_WINDOW = 5  # Duration to monitor the microphone in seconds


def mic_callback(channel):
    """
    Callback function for microphone signal detection.
    """
    print("Signal detected on the receiver's microphone!")


def main():
    GPIO.setmode(GPIO.BCM)

    # Set up the microphone pin
    GPIO.setup(MIC_PIN, GPIO.IN)
    GPIO.add_event_detect(MIC_PIN, GPIO.RISING, callback=mic_callback, bouncetime=200)

    print(
        f"Monitoring the receiver's microphone for {DETECTION_WINDOW} seconds. Please produce a sound signal."
    )

    try:
        # Wait for detection events or until the timer ends
        time.sleep(DETECTION_WINDOW)
        print("Monitoring complete.")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
