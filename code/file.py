#!/usr/bin/python

# interrupt-based GPIO example using LEDs and pushbuttons

import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BOARD)

BTN_G = 11 # G17
BTN_R = 12 # G18
BTN_Y = 13 # G27
BTN_B = 15 # G22

LED_G = 29 # G5
LED_R = 31 # G6
LED_Y = 32 # G12
LED_B = 33 # G13

btn2led = {
	BTN_G: LED_G,
	BTN_R: LED_R,
	BTN_Y: LED_Y,
	BTN_B: LED_B,
}	

GPIO.setwarnings(False) # because I'm using the pins for other things too!
GPIO.setup([BTN_G, BTN_R, BTN_Y, BTN_B], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup([LED_G, LED_R, LED_Y, LED_B], GPIO.OUT, initial=GPIO.HIGH)

# can't add separate callbacks for both rising and falling
#GPIO.add_event_detect(BTN_B, GPIO.RISING, lambda pin: GPIO.output(LED_B, False))
#GPIO.add_event_detect(BTN_B, GPIO.FALLING, lambda pin: GPIO.output(LED_B, True))


def blink_thread():
	x = GPIO.HIGH
	blink = False
	blink_delay = 0.1
	started = time.time()

	#print "blinking"

	while True:
		# yellow and blue change speed
		if GPIO.input(BTN_Y): blink_delay += 0.1
		if GPIO.input(BTN_B): blink_delay -= 0.1
		if blink_delay < 0: blink_delay = 0

		if time.time() - started > 0.5:
			# red or green, after 500 ms, stop
			if GPIO.input(BTN_R) or GPIO.input(BTN_G):
				GPIO.output([LED_G, LED_R, LED_Y, LED_B], True)
				break

		GPIO.output([LED_G, LED_R, LED_Y, LED_B], x)
		if x == GPIO.LOW:
			x = GPIO.HIGH
		else:
			x = GPIO.LOW

		time.sleep(blink_delay)

def handle(pin):
	# light corresponding LED when pushbutton of same color is pressed
	GPIO.output(btn2led[pin], not GPIO.input(pin))

	t = None
	if pin == BTN_G or pin == BTN_R:
		# when green and red pressed simultaneously, enter blink mode
		if GPIO.input(BTN_G) and GPIO.input(BTN_R):
			#print "starting thread"
			t = threading.Thread(target=blink_thread)
			t.daemon = True
			t.start()

GPIO.add_event_detect(BTN_G, GPIO.BOTH, handle)
GPIO.add_event_detect(BTN_R, GPIO.BOTH, handle)
GPIO.add_event_detect(BTN_Y, GPIO.BOTH, handle)
GPIO.add_event_detect(BTN_B, GPIO.BOTH, handle)

# TODO: pause?
while True:
	time.sleep(1e6)