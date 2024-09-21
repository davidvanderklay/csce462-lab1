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


def calculate_frequency(samples, sample_rate):
    zero_crossings = 0
    previous_sample = samples[0]

    for sample in samples[1:]:
        if previous_sample < 1.65 and sample >= 1.65:  # Adjust for centering at 1.65V
            zero_crossings += 1
        previous_sample = sample

    frequency = (zero_crossings / 2) * (sample_rate / len(samples))
    return frequency


def detect_waveform_shape(samples):
    # Normalize samples to range [0, 1]
    normalized_samples = (samples - np.min(samples)) / (
        np.max(samples) - np.min(samples)
    )

    # Calculate the threshold for detecting voltage levels
    threshold = 0.5

    # Count number of peaks and troughs
    peaks = (normalized_samples[:-1] < threshold) & (
        normalized_samples[1:] >= threshold
    )
    troughs = (normalized_samples[:-1] >= threshold) & (
        normalized_samples[1:] < threshold
    )

    num_peaks = np.sum(peaks)
    num_troughs = np.sum(troughs)

    if num_peaks == 0 and num_troughs == 0:
        return "No Voltage"
    elif num_peaks > 2 and num_troughs > 2:
        return "Square Wave"
    elif num_peaks > 2:
        return "Triangle Wave"
    else:
        return "Sine Wave"


def main():
    sample_rate = 1000  # Samples per second
    duration = 5  # Duration in seconds
    num_samples = sample_rate * duration

    samples = []

    print("Collecting samples...")
    for _ in range(num_samples):
        voltage = chan.voltage  # Read the voltage
        samples.append(voltage)  # Store the voltage value
        time.sleep(1.0 / sample_rate)

    frequency = calculate_frequency(samples, sample_rate)
    shape = detect_waveform_shape(np.array(samples))

    print(f"Calculated Frequency: {frequency:.2f} Hz")
    print(f"Detected Waveform Shape: {shape}")

    # Cleanup
    GPIO.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
        GPIO.cleanup()
