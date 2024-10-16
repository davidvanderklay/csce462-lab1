import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import csv

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D4)
# Create the MCP object
mcp = MCP.MCP3008(spi, cs)
# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)


def main():
    sample_rate = 1000  # Reduced sample rate to 1000 Hz
    duration = 5  # Record for 5 seconds
    num_samples = int(sample_rate * duration)
    output_file = "microphone_data.csv"  # Output CSV file

    try:
        with open(output_file, mode="w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Timestamp", "Voltage"])  # Header for CSV

            print(f"Recording {duration} seconds of data at {sample_rate} Hz...")

            start_time = time.time()

            for _ in range(num_samples):
                timestamp = time.time() - start_time
                voltage = chan.voltage
                csvwriter.writerow([timestamp, voltage])
                time.sleep(1 / sample_rate)  # Wait for the next sample

            print(f"Data recording saved to {output_file}")

    except KeyboardInterrupt:
        print("\nExiting program.")


if __name__ == "__main__":
    main()
