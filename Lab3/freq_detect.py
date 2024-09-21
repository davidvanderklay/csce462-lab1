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


def moving_average_filter(samples, window_size=5):
    """Applies a moving average filter to smooth the signal."""
    return np.convolve(samples, np.ones(window_size) / window_size, mode="same")


def detect_waveform_shape(samples):
    threshold = 1.65  # Set the threshold similar to the frequency detection logic

    # Initialize counters for peaks and troughs
    num_peaks = 0
    num_troughs = 0

    previous_sample = samples[0]

    # Iterate over the samples to detect peaks and troughs
    for sample in samples[1:]:
        # Detect peaks (crossing above the threshold from below)
        if previous_sample < threshold and sample >= threshold:
            num_peaks += 1
        # Detect troughs (crossing below the threshold from above)
        elif previous_sample > threshold and sample <= threshold:
            num_troughs += 1

        previous_sample = sample

    # Print debug information
    print(f"Number of Peaks: {num_peaks}, Number of Troughs: {num_troughs}")

    # Determine waveform shape based on the counts of peaks and troughs
    if num_troughs > num_peaks * 1.5:  # Square wave condition
        return "Square Wave"
    elif num_peaks == num_troughs:  # Symmetry suggests sine or triangle wave
        # Differentiate based on further analysis (e.g., slopes or sample symmetry)
        # For now, let's assume sine wave detection can be based on equal peaks/troughs
        return "Sine Wave"
    else:
        return "Triangle Wave"

    return "Unknown Waveform"


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
