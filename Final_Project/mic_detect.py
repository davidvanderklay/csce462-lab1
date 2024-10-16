import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO
import numpy as np

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D4)
# Create the MCP object
mcp = MCP.MCP3008(spi, cs)
# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)


def main():
    sample_rate = 2000  # 2000 Hz
    duration = 0.5  # 0.5 seconds for faster updates
    num_samples = int(sample_rate * duration)

    try:
        while True:
            samples = []
            start_time = time.time()

            for _ in range(num_samples):
                voltage = chan.voltage  # Read voltage from MCP3008
                samples.append(voltage)
                print(f"Voltage: {voltage:.2f} V")  # Print each voltage reading
                time.sleep(1 / sample_rate)  # Sample at the given sample rate

            actual_sample_rate = num_samples / (time.time() - start_time)
            samples = np.array(samples)

            print(f"Actual sample rate: {actual_sample_rate:.2f} Hz")
            print("---")

            time.sleep(0.5)  # Pause between each batch of readings

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
