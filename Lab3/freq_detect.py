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
    # Apply the moving average filter to denoise the signal
    filtered_samples = samples

    # Find the peak: maximum value in the filtered samples
    peak_index = np.argmax(filtered_samples)
    peak_value = filtered_samples[peak_index]

    # Analyze slopes before the peak
    num_points_for_slope = 2  # Number of points to calculate slope over
    left_slope = None

    if peak_index > num_points_for_slope:
        # Calculate the slope to the left of the peak using 2 points
        left_slope = (
            filtered_samples[peak_index]
            - filtered_samples[peak_index - num_points_for_slope]
        ) / num_points_for_slope

    print(f"Peak Value: {peak_value}, Peak Index: {peak_index}")
    print(f"Left Slope: {left_slope:.4f} (over {num_points_for_slope} points)")

    # Classification based on the left slope
    if left_slope is not None:
        if abs(left_slope) < 0.15:  # Less than 0.24 -> Triangle wave
            return "Triangle Wave"
        else:  # Greater than or equal to 0.24 -> Sine wave
            return "Sine Wave"

    return "Unknown Waveform"


def main():
    sample_rate = 10000  # Samples per second
    duration = 3  # Duration in seconds
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
