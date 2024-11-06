import RPi.GPIO as GPIO
import time

# Configuration
MIC_PIN = 6  # GPIO pin connected to Microphone 2
DETECTION_WINDOW = 5  # Duration to monitor the microphone in seconds


def mic_callback(channel):
    """
    Callback function for signal detection on Microphone 2.
    """
    print("Signal detected on Microphone 2 (GPIO 6)!")


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MIC_PIN, GPIO.IN)
    GPIO.add_event_detect(M_PIN, GPIO.RISING, callback=mic_callback, bouncetime=200)

    print(f"Monitoring Microphone 2 on GPIO {MIC_PIN} for {DETECTION_WINDOW} seconds.")

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
