import RPi.GPIO as GPIO
from time import sleep


PIN = 18  # use pin that we want
FREQUENCY = 1e5  # 100kHz
PERIOD = 1 / FREQUENCY

def setup():
    """Setup the GPIO pin."""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

def square_wave():
    """Generate a square waveform."""
    while True:
        GPIO.output(PIN, GPIO.HIGH)
        sleep(PERIOD / 2)
        GPIO.output(PIN, GPIO.LOW)  
        sleep(PERIOD / 2) 

if __name__ == '__main__':
    setup()
    try:
        square_wave()
    except KeyboardInterrupt:
        print("Program interrupted by user")
    finally:
        GPIO.cleanup()  # Clean up GPIO settings
