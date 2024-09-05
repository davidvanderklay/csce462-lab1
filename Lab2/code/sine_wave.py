import time
import math
import board
import busio
from adafruit_mcp4725 import MCP4725

# Create an I2C bus object and initialize the DAC
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c)

def sin_wave():
    t = 0.0
    tStep = 0.05
    while True:
        # Calculate the voltage value for the sine wave
        voltage = 2048 * (1.0 + 0.5 * math.sin(2 * math.pi * t))
        # Set the DAC voltage
        dac.value = int(voltage)
        # Increment time
        t += tStep
        # Sleep for a short duration
        time.sleep(0.0005)

if __name__ == "__main__":
    try:
        sin_wave()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        # Optionally, you can add cleanup code here if needed
        pass
