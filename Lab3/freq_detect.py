import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

# spi, adc setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# parameters for detecting wave
sampling_rate = 1000  # Hz
samples = 1000  # Increased number of samples to stabilize readings
threshold = 0.2  # Threshold for signal variation


# Butterworth low-pass filter to remove high-frequency noise
def butter_lowpass_filter(data, cutoff=100, fs=sampling_rate, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)
    return y


# Sample the waveform data
def sample_waveform():
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


# Enhanced peak detection
def detect_peaks(data):
    # Apply stronger filtering
    filtered_data = butter_lowpass_filter(data)

    # Detect peaks with a minimum prominence to filter noise
    peaks, _ = find_peaks(filtered_data, prominence=0.05)  # Adjust prominence as needed

    return peaks, filtered_data


def calculate_frequency(data):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Detect peaks and valleys to capture both positive and negative cycles
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1
    valleys = (np.diff(np.sign(np.diff(denoised_data))) > 0).nonzero()[0] + 1

    # Combine peaks and valleys for full waveform cycle detection
    all_extrema = sorted(np.concatenate((peaks, valleys)))

    # Ensure that we're counting complete cycles (i.e., both peaks and valleys)
    if len(all_extrema) >= 2:
        # Calculate the period based on the distance between every second extremum
        full_cycle_periods = np.diff(
            all_extrema[::2]
        )  # Every second extremum represents a full cycle

        # Calculate the average period and frequency
        period = np.mean(full_cycle_periods) / sampling_rate
        frequency = 1 / period
        print(f"Detected extrema (peaks and valleys): {all_extrema}")
        print(f"Calculated full cycle period: {period} seconds")
        return frequency

    return None


#
# Main loop
last_frequency = None

while True:
    # Get the waveform data
    data = sample_waveform()

    # Detect peaks and apply filtering
    peaks, filtered_data = detect_peaks(data)

    # Calculate and print frequency if stable
    frequency = calculate_frequency(peaks)

    if frequency:
        # Only print when the frequency changes significantly (optional threshold for "major changes")
        if last_frequency is None or abs(frequency - last_frequency) > 1:
            print(f"Frequency: {frequency:.2f} Hz")
            print(f"Peaks for frequency calculation: {peaks}")
            last_frequency = frequency

    # Small pause to save CPU
    time.sleep(0.5)
