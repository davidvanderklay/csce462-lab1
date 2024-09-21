import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# SPI, ADC setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# Parameters for detecting wave
sampling_rate = 500  # Hz
samples = 1000  # Number of samples to analyze
threshold = 0.2  # Threshold for signal variation


# Denoising using a moving average
def denoise_signal(signal, window_size=20):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def sample_waveform():
    # Sample the ADC for readings
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


# Frequency calculation from sampled data
def calculate_frequency(data, sampling_rate=500, threshold=0.05):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Detect peaks (local maxima) and valleys (local minima)
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1
    valleys = (np.diff(np.sign(np.diff(denoised_data))) > 0).nonzero()[0] + 1

    # Filter out insignificant peaks and valleys based on threshold
    significant_peaks = [
        p for p in peaks if denoised_data[p] > (np.max(denoised_data) * threshold)
    ]
    significant_valleys = [
        v for v in valleys if denoised_data[v] < (np.min(denoised_data) * threshold)
    ]

    # Combine peaks and valleys for full cycle detection
    all_extrema = sorted(np.concatenate((significant_peaks, significant_valleys)))

    # Ensure that we're counting complete cycles
    if len(all_extrema) >= 2:
        # Calculate the period based on the distance between every second extremum (representing full cycles)
        full_cycle_periods = np.diff(all_extrema[::2])

        # Calculate the average period and frequency
        period = np.mean(full_cycle_periods) / sampling_rate
        frequency = 1 / period
        return frequency

    return None


def detect_waveform_shape(data):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Calculate the average value to determine if the signal is near zero
    average_value = np.mean(denoised_data)

    # Identify significant peaks
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1

    # Early exit if not enough peaks
    if len(peaks) < 2:
        return "Flat Line"

    # Analyze the first peak and the subsequent values
    first_peak = peaks[0]
    rising_edges = np.diff(denoised_data[:first_peak]) > 0
    falling_edges = np.diff(denoised_data[first_peak:]) < 0

    if np.all(rising_edges) and np.all(falling_edges):
        return "Square Wave"
    elif np.any(rising_edges) and np.any(falling_edges):
        return "Triangle Wave"
    elif average_value < 0.05:  # Adjust threshold as needed for low signals
        return "Empty Signal"
    else:
        return "Sine Wave"


# Main loop
last_waveform = None
while True:
    data = sample_waveform()

    # Calculate frequency
    frequency = calculate_frequency(data)
    if frequency:
        print(f"Frequency: {frequency:.2f} Hz")

    # Detect waveform shape
    waveform = detect_waveform_shape(data)

    # Print only frequency and shape detected
    print(f"Detected waveform: {waveform}")

    # Small pause to save CPU
    time.sleep(0.5)
