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
samples = 2000  # Number of samples to analyze
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


def detect_waveform_shape(data, low_voltage_threshold=0.1):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Check for low voltage
    if np.mean(denoised_data) < low_voltage_threshold:
        return "No Voltage"

    # Detect peaks and valleys
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1
    valleys = (np.diff(np.sign(np.diff(denoised_data))) > 0).nonzero()[0] + 1

    # Ensure there are enough peaks and valleys to analyze
    if len(peaks) < 2 or len(valleys) < 2:
        return "Unknown Waveform (Not enough features)"

    # Calculate intervals
    peak_intervals = np.diff(peaks)
    valley_intervals = np.diff(valleys)

    # Analyze the ratios of intervals
    if len(peak_intervals) > 1 and len(valley_intervals) > 1:
        avg_peak_interval = np.mean(peak_intervals)
        avg_valley_interval = np.mean(valley_intervals)

        # Check for square wave characteristics
        if np.abs(avg_peak_interval - avg_valley_interval) < 0.2 * avg_peak_interval:
            return "Square Wave"

    # If square wave isn't detected, check for triangle wave
    if len(peaks) > 1 and len(valleys) > 1:
        peak_amplitudes = denoised_data[peaks]
        valley_amplitudes = denoised_data[valleys]

        if np.all(np.diff(peak_amplitudes) > 0) and np.all(
            np.diff(valley_amplitudes) < 0
        ):
            return "Triangle Wave"

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
