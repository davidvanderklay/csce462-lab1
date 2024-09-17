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
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)
chan0 = AnalogIn(mcp, MCP.P0)

# parameters for detecting wave
sampling_rate = 1000  # Hz
samples = 500  # Number of samples to analyze
threshold = 0.2  # Threshold for signal variation


def sample_waveform():
    # sampel the adc for readings
    data = []
    for _ in range(samples):
        data.append(chan0.voltage)
        time.sleep(1 / sampling_rate)
    return np.array(data)


def detect_waveform_shape(data):
    # return shape based on characteristics
    max_val = np.max(data)
    min_val = np.min(data)
    amplitude = max_val - min_val
    if amplitude == 0:
        return "Unknown Waveform (Flat Line)"
    # makes it so signal data varies from 0 to 1
    normalized_data = (data - min_val) / amplitude

    # return square if flat regions seem to exist around 0 and 1
    if np.all(normalized_data < 0.5 + threshold) and np.all(
        normalized_data > 0.5 - threshold
    ):
        return "Square Wave"
    # return sine if sign of second derivative not changing rapidly
    elif np.all(np.abs(np.diff(np.sign(np.diff(normalized_data)))) <= 1):
        return "Sine Wave"
    # return triangle increases and decreases about linear
    elif np.all(np.diff(normalized_data) > 0) or np.all(np.diff(normalized_data) < 0):
        return "Triangle Wave"
    else:
        return "Unknown Waveform"


def calculate_frequency(data):
    # check for when the second derivative is negative - local maxima
    peaks = (np.diff(np.sign(np.diff(data))) < 0).nonzero()[0] + 1
    # look for at least 2 peaks to compute period
    if len(peaks) >= 2:
        period = np.mean(np.diff(peaks)) / sampling_rate
        # compute frequency from period
        frequency = 1 / period
        return frequency
    return None


# loop forever very cool
last_waveform = None
while True:
    # call the sample function to get data
    data = sample_waveform()

    # loop shape detection
    waveform = detect_waveform_shape(data)

    # check if changes are made to the waveform
    if waveform != last_waveform:
        print(f"Detected waveform: {waveform}")
        last_waveform = waveform

    # compute frequency
    frequency = calculate_frequency(data)
    if frequency:
        print(f"Frequency: {frequency:.2f} Hz")

    # pause between readings to save cpu
    time.sleep(0.5)
