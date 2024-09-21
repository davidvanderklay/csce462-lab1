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
    # denoised_data = denoise_signal(data)
    denoised_data = data

    # Detect zero-crossings for more accurate frequency measurement
    zero_crossings = np.where(np.diff(np.sign(denoised_data)))[0]
    print(f"Zero Crossings: {zero_crossings}")  # Debugging output

    if len(zero_crossings) < 2:
        return None  # Not enough zero crossings to calculate frequency

    # Calculate the periods between zero crossings
    crossing_intervals = np.diff(zero_crossings)

    # Calculate the average period
    if len(crossing_intervals) > 0:
        average_period = np.mean(crossing_intervals) / sampling_rate
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
