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
    threshold = 1.65  # Voltage threshold to detect peaks and troughs

    num_peaks = 0
    num_troughs = 0
    peak_slopes = []

    previous_sample = samples[0]
    previous_index = 0  # To track the indices for slope calculation

    slopes = np.diff(samples)  # Calculate slopes between consecutive samples

    # Iterate through the samples to detect peaks and troughs
    for i, sample in enumerate(samples[1:], start=1):
        if previous_sample < threshold and sample >= threshold:
            # Peak detected, increment counter and store slopes around the peak
            num_peaks += 1
            if i > 0 and i < len(slopes) - 1:
                peak_slopes.append((slopes[i - 1], slopes[i]))
        elif previous_sample > threshold and sample <= threshold:
            # Trough detected, increment counter
            num_troughs += 1

        previous_sample = sample
        previous_index = i

    # Print debug information for peaks and troughs
    print(f"Number of Peaks: {num_peaks}, Number of Troughs: {num_troughs}")

    # Analyze the slopes around peaks
    if peak_slopes:
        avg_abs_peak_slope = np.mean([abs(slope[1]) for slope in peak_slopes])
        max_peak_slope = np.max([slope[1] for slope in peak_slopes])
        print(
            f"Average Absolute Slope at Peaks: {avg_abs_peak_slope:.4f}, Max Slope at Peaks: {max_peak_slope:.4f}"
        )

    # Determine waveform shape based on peak and slope analysis
    if num_troughs > num_peaks * 1.5:  # Square wave condition
        return "Square Wave"
    elif num_peaks == num_troughs:  # Symmetry suggests sine or triangle wave
        if avg_abs_peak_slope < 0.1:  # Sine wave: low slope around peaks
            return "Sine Wave"
        else:  # Higher slope might suggest a triangle wave
            return "Triangle Wave"
    else:
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
