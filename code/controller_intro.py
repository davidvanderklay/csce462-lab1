import RPi.GPIO as GPIO
from time import sleep

# pin initialization - change based on what we use on board
segments = {
    'A': 13,
    'B': 6,
    'C': 16,
    'D': 20,
    'E': 21,
    'F': 19,
    'G': 26
}

"""
TODO:
* connect segment G , needs more jumper wires
* connect ground to the seven segment display
* connect both leds / traffic lights based on the pin layouts
* connect the button pin with a pull down resistor (or modify code accordingly)
"""

# hex values for what should be enabled
dat = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
TL1 = {'green': 5, 'blue': 22, 'red': 27}
TL2 = {'green': 17, 'blue': 4, 'red': 18}
BUTTON_PIN = 23

def setup():
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    # setup segments
    for pin in segments.values():
        GPIO.setup(pin, GPIO.OUT)
    # setup traffic lights
    for color in TL1.values():
        GPIO.setup(color, GPIO.OUT)
    for color in TL2.values():
        GPIO.setup(color, GPIO.OUT)
    # button setup
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # sets traffic light 2 to green and nothing else
    GPIO.output(TL2['green'], GPIO.HIGH)
    GPIO.output(TL1['green'], GPIO.LOW)
    GPIO.output(TL1['blue'], GPIO.LOW)
    GPIO.output(TL1['red'], GPIO.HIGH)
    GPIO.output(TL2['blue'], GPIO.LOW)
    GPIO.output(TL2['red'], GPIO.LOW)
    

def PORT(pin):
    GPIO.output(segments['A'], pin & 0x01)
    GPIO.output(segments['B'], pin & 0x02)
    GPIO.output(segments['C'], pin & 0x04)
    GPIO.output(segments['D'], pin & 0x08)
    GPIO.output(segments['E'], pin & 0x10)
    GPIO.output(segments['F'], pin & 0x20)
    GPIO.output(segments['G'], pin & 0x40)

def countdown():
    # counts from 9 to 0 with 1 second increment
    for i in range(9, -1, -1):
        PORT(dat[i])
        if i <= 4:
            # Step 3: When countdown reaches 4, TL1 flashes blue until 0
            GPIO.output(TL1['green'], GPIO.LOW)
            blink_light(TL1['blue'], 1)
        sleep(1)

    # End of countdown, set TL1 red, TL2 green
    GPIO.output(TL1['red'], GPIO.HIGH)
    GPIO.output(TL2['red'], GPIO.LOW)
    GPIO.output(TL2['green'], GPIO.HIGH)

def handle_button_press():
    """Handle the sequence of events when the button is pressed."""
    # Step 1: TL2 turns blue, blinks 3 times, then turns red
    GPIO.output(TL2['green'], GPIO.LOW)
    blink_light(TL2['blue'], 3)
    GPIO.output(TL2['blue'], GPIO.LOW)
    GPIO.output(TL2['red'], GPIO.HIGH)
    
    # Step 2: TL1 turns green, start countdown from 9 to 0
    GPIO.output(TL1['green'], GPIO.HIGH)
    countdown()

def poll_button():
    # polling method
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:  # button is pressed by something
            handle_button_press()
            sleep(20)  # cooldown as lights change
        sleep(0.1)  # delay to minimize cpu utilization

def interrupt_handler(channel):
    # interrupt handler
    handle_button_press()
    sleep(20)  # 20-second cooldown

def setup_interrupt():
    # interrupt setup
    GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, bouncetime=300)
    GPIO.add_event_callback(BUTTON_PIN, handle_button_press)


def blink_light(pin, times):
    # blinks led times times
    for _ in range(times):
        GPIO.output(pin, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(pin, GPIO.LOW)
        sleep(0.5)

if __name__ == '__main__':
    setup()
    try:
        # poll_button()  # Polling method
        setup_interrupt()  # Interrupt method
        while True:
            sleep(1)  # keeps running without draining resources
    except KeyboardInterrupt:
        print("Keyboard Interrupt Detected")
    finally:
        GPIO.cleanup()