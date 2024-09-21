import os
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np

# SPI and MCP3008 setup
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)  # Chip select pin
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)  # Using channel 0


def denoise_signal(signal, window_size=20):
    """Denoise the signal using a moving average."""
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def calculate_frequency(data, sampling_rate=500):
    """Calculate the frequency of the signal from the sampled data."""
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Detect peaks
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1

    if len(peaks) < 2:
        return None  # Not enough peaks to calculate frequency

    # Calculate the periods between peaks
    peak_intervals = np.diff(peaks)

    # Calculate the average period
    if len(peak_intervals) > 0:
        average_period = np.mean(peak_intervals) / sampling_rate
        frequency = 1 / average_period
        return frequency

    return None


def sample_waveform(chan, samples=1000, sampling_rate=500):
    """Sample the waveform from the ADC."""
    data = []
    for _ in range(samples):
        data.append(chan.voltage)  # Read voltage from the ADC channel
        time.sleep(1 / sampling_rate)  # Wait for the sampling period
    return np.array(data)


def detect_frequency(chan, samples=1000, sampling_rate=500):
    data = sample_waveform(chan, samples, sampling_rate)
    frequency = calculate_frequency(data, sampling_rate)

    if frequency:
        print(f"Detected Frequency: {frequency:.2f} Hz")
    else:
        print("Frequency could not be determined.")


# Run the frequency detection
detect_frequency(chan)
