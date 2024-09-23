# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0, MCP.P1)

try:
    # continuously read values until user interrupts with Ctrl + C
    while True:
        print("Raw ADC Value: ", chan.value)
        print("ADC Voltage: " + str(chan.voltage) + "V")
        time.sleep(0.001)  # sleep for 0.5 seconds between readings for readability

except KeyboardInterrupt:
    print("\nExiting program.")
    GPIO.cleanup()
