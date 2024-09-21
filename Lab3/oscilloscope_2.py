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

# Parameters for detecting frequency
sampling_rate = 1000  # Hz
samples = 500  # Number of samples to analyze
low_voltage_threshold = 0.01  # Threshold to detect an "empty" waveform (low voltage)


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


# Function to sample the ADC for readings
def sample_waveform():
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


# Frequency detection
def calculate_frequency(data):
    max_val = np.max(data)
    min_val = np.min(data)
    amplitude = max_val - min_val

    # Check for "empty" waveform (low amplitude)
    if amplitude < low_voltage_threshold:
        print("Empty waveform detected: low amplitude signal.")
        return None

    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Peak detection for frequency calculation
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1

    # Calculate frequency if enough peaks are detected
    if len(peaks) >= 2:
        period = np.mean(np.diff(peaks)) / sampling_rate
        frequency = 1 / period
        print(f"Peaks for frequency calculation: {peaks}")
        print(f"Calculated period: {period}")
        return frequency
    else:
        print("Insufficient peaks for frequency calculation.")
        return None


# Main loop
last_frequency = None
while True:
    data = sample_waveform()

    # Calculate frequency
    frequency = calculate_frequency(data)

    # Print only if frequency changes
    if frequency and frequency != last_frequency:
        print(f"Frequency: {frequency:.2f} Hz")
        last_frequency = frequency

    # Small pause to save CPU
    time.sleep(0.5)
