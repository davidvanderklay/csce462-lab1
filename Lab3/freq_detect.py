import numpy as np
import time


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
        data.append(chan.voltage)  # Replace with correct ADC read method
        time.sleep(1 / sampling_rate)
    return np.array(data)


# Main function to run frequency detection
def detect_frequency(chan, samples=1000, sampling_rate=500):
    data = sample_waveform(chan, samples, sampling_rate)
    frequency = calculate_frequency(data, sampling_rate)

    if frequency:
        print(f"Detected Frequency: {frequency:.2f} Hz")
    else:
        print("Frequency could not be determined.")


# Example usage:
# Assuming `chan` is your AnalogIn channel for the MCP3008
# detect_frequency(chan)
