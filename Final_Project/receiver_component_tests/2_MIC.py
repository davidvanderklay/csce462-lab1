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

    try:
        # Set up the microphone pin
        GPIO.setup(MIC_PIN, GPIO.IN)

        # Ensure no prior event detection is set on this pin
        if GPIO.event_detected(MIC_PIN):
            GPIO.remove_event_detect(MIC_PIN)

        # Add event detection for microphone pin
        GPIO.add_event_detect(
            MIC_PIN, GPIO.RISING, callback=mic_callback, bouncetime=200
        )

        print(
            f"Monitoring the receiver's microphone for {DETECTION_WINDOW} seconds. Please produce a sound signal."
        )

        # Wait for detection events or until the timer ends
        time.sleep(DETECTION_WINDOW)
        print("Monitoring complete.")
    except RuntimeError as e:
        print(f"RuntimeError encountered: {e}")
        print("Ensure the GPIO pin is not already in use or locked by another process.")
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")


if __name__ == "__main__":
    main()
