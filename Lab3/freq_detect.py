import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# MCP3008 setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# Parameters for sampling and analysis
sampling_rate = 500  # Hz, adjusted for 10-100 Hz signal range
samples = 1000  # Number of samples to collect
threshold = 0.05  # Threshold for peak detection to ignore small variations


# Denoising using a moving average
def denoise_signal(signal, window_size=20):  # Optimized for 10-100 Hz signals
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


# MCP3008 data sampling
def sample_waveform():
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)  # Sampling delay
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
        print(f"Detected significant extrema (peaks and valleys): {all_extrema}")
        print(f"Calculated full cycle period: {period:.5f} seconds")
        return frequency

    return None


# Main loop
while True:
    data = sample_waveform()

    # Calculate and print frequency
    frequency = calculate_frequency(data, sampling_rate)
    if frequency:
        print(f"Detected frequency: {frequency:.2f} Hz")

    # Small pause to avoid overwhelming the CPU
    time.sleep(0.5)
