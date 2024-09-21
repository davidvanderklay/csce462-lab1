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
cs = digitalio.DigitalInOut(board.D5)

# Create the MCP object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

# Threshold for low voltage detection
LOW_VOLTAGE_THRESHOLD = 0.5
SAMPLE_RATE = 2000  # Increased samples per second
DURATION = 5  # Duration in seconds


def moving_average(samples, window_size=5):
    if len(samples) < window_size:
        return samples
    return np.convolve(samples, np.ones(window_size) / window_size, mode="valid")


def calculate_frequency(samples, sample_rate):
    zero_crossings = 0
    previous_sample = samples[0]

    for sample in samples[1:]:
        if previous_sample < 1.65 and sample >= 1.65:
            zero_crossings += 1
        previous_sample = sample

    frequency = (zero_crossings / 2) * (sample_rate / len(samples))
    return frequency


def identify_waveform(samples):
    if len(samples) < 2:
        return "Unknown"

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
    num_samples = SAMPLE_RATE * DURATION
    samples = []

    print("Collecting samples...")
    for _ in range(num_samples):
        voltage = chan.voltage  # Read the voltage

        if voltage < LOW_VOLTAGE_THRESHOLD:
            continue  # Ignore low voltage readings

        samples.append(voltage)  # Store the voltage value
        time.sleep(1.0 / SAMPLE_RATE)

    if not samples:
        print("No valid waveform detected.")
        return

    # Apply moving average to smooth out noise
    smoothed_samples = moving_average(samples)

    frequency = calculate_frequency(smoothed_samples, SAMPLE_RATE)
    waveform_shape = identify_waveform(smoothed_samples)

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
