import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# SPI and ADC setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# Parameters
sampling_rate = 1000  # Hz
samples = 500  # Number of samples to analyze
empty_waveform_threshold = 0.05  # Voltage threshold to detect empty signal


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


# Sampling the ADC
def sample_waveform():
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


# Empty waveform detection
def is_empty_waveform(data):
    # Check if all values are below a certain low voltage threshold
    return np.max(data) < empty_waveform_threshold


# Calculate frequency by finding valid peaks
def calculate_frequency(data):
    denoised_data = denoise_signal(data)

    # Peak detection with threshold to filter noise
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1

    # Filter out peaks that are too close to each other
    min_peak_distance = int(
        sampling_rate / 100
    )  # Ignore peaks closer than 10ms (for 100 Hz or lower)
    valid_peaks = [peaks[0]]  # Start with the first peak

    for i in range(1, len(peaks)):
        if peaks[i] - valid_peaks[-1] >= min_peak_distance:
            valid_peaks.append(peaks[i])

    if len(valid_peaks) >= 2:
        period = np.mean(np.diff(valid_peaks)) / sampling_rate
        frequency = 1 / period
        print(f"Valid peaks for frequency calculation: {valid_peaks}")
        print(f"Calculated period: {period}")
        return frequency
    else:
        return None


# Main loop
last_frequency = None
while True:
    data = sample_waveform()

    # Detect empty waveform
    if is_empty_waveform(data):
        print("Detected empty waveform (low voltage)")
        last_frequency = None
        continue

    # Calculate and print frequency
    frequency = calculate_frequency(data)
    if frequency and (
        last_frequency is None or abs(frequency - last_frequency) > 1
    ):  # Print only for significant changes
        print(f"Frequency: {frequency:.2f} Hz")
        last_frequency = frequency

    # Small pause to save CPU
    time.sleep(0.5)
