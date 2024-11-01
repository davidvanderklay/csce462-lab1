import RPi.GPIO as GPIO
import time

# GPIO pin setup
MIC_PIN = 5  # Input pin connected to the microphone
SPEAKER_PIN = 18  # Output pin connected to the speaker


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MIC_PIN, GPIO.IN)
    GPIO.setup(SPEAKER_PIN, GPIO.OUT)
    GPIO.add_event_detect(MIC_PIN, GPIO.RISING, callback=mic_callback)


def cleanup_gpio():
    GPIO.cleanup()


def mic_callback(channel):
    print("Signal detected. Sending response beep.")
    emit_beep()


def emit_beep(frequency=5000, duration=0.1):
    pwm = GPIO.PWM(SPEAKER_PIN, frequency)
    pwm.start(50)  # 50% duty cycle
    time.sleep(duration)
    pwm.stop()


def main():
    init_gpio()
    try:
        print("Receiver is active. Waiting for signal...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    finally:
        cleanup_gpio()


if __name__ == "__main__":
    main()
