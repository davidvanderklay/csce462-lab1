import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
import time
import RPi.GPIO as GPIO

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D5)

# Create the MCP object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

# Threshold for low voltage detection
LOW_VOLTAGE_THRESHOLD = 0.1
SAMPLE_RATE = 1000  # Samples per second
DURATION = 5  # Duration in seconds


def calculate_frequency(samples):
    zero_crossings = 0
    previous_sample = samples[0]
    last_crossing_time = 0
    crossing_times = []

    for i, sample in enumerate(samples[1:], start=1):
        if previous_sample < 1.65 and sample >= 1.65:  # Rising edge detected
            zero_crossings += 1
            crossing_times.append(i)  # Store index of crossing
        previous_sample = sample

    # Calculate frequency based on time between crossings
    if len(crossing_times) < 2:
        return 0  # Not enough crossings to calculate frequency

    time_intervals = np.diff(crossing_times)  # Time between zero crossings
    average_period = np.mean(time_intervals) / SAMPLE_RATE  # Convert to seconds
    frequency = 1 / average_period if average_period > 0 else 0  # Calculate frequency
    return frequency


def identify_waveform(samples):
    peaks = np.where(np.diff(np.sign(np.diff(samples))) < 0)[0] + 1
    troughs = np.where(np.diff(np.sign(np.diff(samples))) > 0)[0] + 1

    peak_count = len(peaks)
    trough_count = len(troughs)

    if peak_count == trough_count and peak_count > 0:
        return "Square Wave"
    elif peak_count >= 2 and trough_count >= 2:
        return "Triangle Wave"
    elif peak_count == 1 and trough_count == 1:
        return "Sine Wave"
    else:
        return "Unknown"


def main():
    samples = []

    print("Collecting samples...")
    for _ in range(SAMPLE_RATE * DURATION):
        voltage = chan.voltage  # Read the voltage

        if voltage < LOW_VOLTAGE_THRESHOLD:
            continue  # Ignore low voltage readings

        samples.append(voltage)  # Store the voltage value
        time.sleep(1.0 / SAMPLE_RATE)

    if not samples:
        print("No valid waveform detected.")
        return

    frequency = calculate_frequency(samples)
    waveform_shape = identify_waveform(samples)

    print(f"Detected Waveform: {waveform_shape}")
    print(f"Calculated Frequency: {frequency:.2f} Hz")

    # Cleanup
    GPIO.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
        GPIO.cleanup()
