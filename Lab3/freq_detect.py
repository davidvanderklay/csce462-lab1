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

    # Calculate the first derivative (slope) to analyze behavior around peaks
    slopes = np.diff(normalized_samples)

    # Print basic statistics for slopes
    print(f"Total Number of Slopes: {len(slopes)}")
    print(
        f"Max Slope: {np.max(slopes):.4f}, Min Slope: {np.min(slopes):.4f}, Average Slope: {np.mean(slopes):.4f}"
    )

    # Check for zero crossings to find peaks and their characteristics
    peak_indices = np.where((slopes[:-1] > 0) & (slopes[1:] < 0))[0] + 1  # Peaks
    trough_indices = np.where((slopes[:-1] < 0) & (slopes[1:] > 0))[0] + 1  # Troughs

    num_peaks = len(peak_indices)
    num_troughs = len(trough_indices)

    # Analyze peak characteristics
    if num_peaks == 0 and num_troughs == 0:
        return "No Voltage"

    # Calculate slopes at peaks
    peak_slopes = []
    for index in peak_indices:
        if index > 0 and index < len(slopes) - 1:
            peak_slopes.append((slopes[index - 1], slopes[index]))

    # Print summary of peak slopes
    print(f"Number of Peaks: {num_peaks}, Number of Troughs: {num_troughs}")
    if peak_slopes:
        avg_peak_slope = np.mean([slope[1] for slope in peak_slopes])
        print(f"Average Slope at Peaks: {avg_peak_slope:.4f}")

    # Determine waveform shape based on slope characteristics
    square_wave_detected = any(
        slope[0] > 0.1 and slope[1] < -0.1 for slope in peak_slopes
    )
    if square_wave_detected:
        return "Square Wave"

    # Triangle wave characteristics
    if num_peaks > num_troughs:
        return "Triangle Wave"

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
