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
sampling_rate = 500  # Hz, optimal for 10-100 Hz signals
samples = 1000  # Number of samples to analyze


def sample_waveform():
    # Sample the ADC for readings
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def calculate_frequency(data):
    # Find peaks for frequency calculation
    peaks = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1
    if len(peaks) >= 2:
        period = np.mean(np.diff(peaks)) / sampling_rate
        frequency = 1 / period
        return frequency
    return None


def detect_waveform_shape(data):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Find peaks and valleys
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

    # Check for flat regions for square waves
    high_threshold = 0.8 * np.max(denoised_data)
    low_threshold = 0.2 * np.min(denoised_data)
    high_vals = np.where(denoised_data > high_threshold)[0]
    low_vals = np.where(denoised_data < low_threshold)[0]

    # Determine waveform shape
    if len(high_vals) > len(low_vals) * 1.5 and len(low_vals) > len(high_vals) * 1.5:
        return "Square Wave"
    elif np.abs(rising_slope) < 0.2 and np.abs(falling_slope) < 0.2:
        return "Triangle Wave"
    else:
        return "Sine Wave"


# Main loop
last_waveform = None
while True:
    data = sample_waveform()

    # Calculate frequency
    frequency = calculate_frequency(data)
    if frequency:
        print(f"Detected frequency: {frequency:.2f} Hz")

    # Detect waveform shape
    waveform = detect_waveform_shape(data)
    if waveform != last_waveform:
        print(f"Detected waveform: {waveform}")
        last_waveform = waveform

    time.sleep(0.5)  # Adjust for CPU saving
