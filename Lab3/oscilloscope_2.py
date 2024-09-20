import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# spi, adc setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# parameters for detecting wave
sampling_rate = 1000  # Hz
samples = 500  # Number of samples to analyze
threshold = 0.2  # Threshold for signal variation


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def sample_waveform():
    # sample the adc for readings
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


def detect_waveform_shape(data):
    max_val = np.max(data)
    min_val = np.min(data)
    amplitude = max_val - min_val

    if amplitude == 0:
        return "Unknown Waveform (Flat Line)"

    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Peak detection
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1
    valleys = (np.diff(np.sign(np.diff(denoised_data))) > 0).nonzero()[0] + 1

    if len(peaks) < 2 or len(valleys) < 2:
        return "Unknown Waveform (Not enough peaks)"

    # Analyze slopes
    rising_slope = np.mean(
        np.diff(denoised_data[: peaks[0]])
    )  # Slope before first peak
    falling_slope = np.mean(
        np.diff(denoised_data[peaks[0] :])
    )  # Slope after first peak

    print(f"Peaks detected at indices: {peaks}")
    print(f"Valleys detected at indices: {valleys}")
    print(f"Rising slope: {rising_slope}")
    print(f"Falling slope: {falling_slope}")

    # Detect waveform type based on slopes
    if np.abs(rising_slope) < 0.2 and np.abs(falling_slope) < 0.2:
        return "Triangle Wave"
    elif np.abs(rising_slope) > 0.5 and np.abs(falling_slope) > 0.5:
        return "Square Wave"
    else:
        return "Sine Wave"


def calculate_frequency(data):
    # check for local maxima by detecting negative second derivatives
    peaks = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1
    if len(peaks) >= 2:
        period = np.mean(np.diff(peaks)) / sampling_rate
        frequency = 1 / period
        print(f"Peaks for frequency calculation: {peaks}")
        print(f"Calculated period: {period}")
        return frequency
    return None


# Main loop
last_waveform = None
while True:
    data = sample_waveform()

    # Detect waveform shape
    waveform = detect_waveform_shape(data)

    # Print only if waveform changes
    if waveform != last_waveform:
        print(f"Detected waveform: {waveform}")
        last_waveform = waveform

    # Calculate and print frequency
    frequency = calculate_frequency(data)
    if frequency:
        print(f"Frequency: {frequency:.2f} Hz")

    # Small pause to save CPU
    time.sleep(0.5)
