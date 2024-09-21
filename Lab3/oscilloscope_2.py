import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
from scipy.signal import find_peaks

# spi, adc setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# parameters for detecting wave
sampling_rate = 500  # Hz (adjusted for signals < 100Hz)
samples = 1000  # Increased number of samples for better detection


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def sample_waveform():
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


def calculate_frequency(data):
    # Apply denoising
    denoised_data = denoise_signal(data)

    # Peak detection with prominence to avoid small fluctuations
    peaks, properties = find_peaks(denoised_data, prominence=0.05)
    if len(peaks) >= 2:
        periods = np.diff(peaks) / sampling_rate
        frequency = 1 / np.mean(periods)
        print(f"Peaks for frequency calculation: {peaks}")
        print(f"Calculated period: {np.mean(periods)} seconds")
        return frequency
    return None


# Detect empty waveform based on low voltage
def detect_empty_waveform(data):
    if np.max(data) < 0.05:  # Low threshold for detecting empty waveform
        return True
    return False


# Main loop
last_frequency = None
while True:
    data = sample_waveform()

    # Detect empty waveform
    if detect_empty_waveform(data):
        print("Detected empty waveform (low voltage)")
        time.sleep(0.5)
        continue

    # Calculate and print frequency only if there's a major change
    frequency = calculate_frequency(data)
    if frequency and (last_frequency is None or abs(frequency - last_frequency) > 5):
        print(f"Frequency: {frequency:.2f} Hz")
        last_frequency = frequency

    # Small pause to save CPU
    time.sleep(0.5)
