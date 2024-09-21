import numpy as np


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def calculate_frequency(data, sampling_rate=1000):
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


# Example data sampling simulation (replace with real ADC data in actual use case)
def sample_waveform():
    # Simulating a sample waveform, replace this with actual MCP3008 sampling logic
    time = np.linspace(0, 1, 1000)
    frequency = 50  # 50 Hz signal
    amplitude = 3.3
    data = amplitude * np.sin(2 * np.pi * frequency * time)  # Example sine wave
    return data


# Testing with example data
sampling_rate = 1000  # Adjust to match your actual sampling rate
data = sample_waveform()

# Calculate frequency
frequency = calculate_frequency(data, sampling_rate)
if frequency:
    print(f"Detected frequency: {frequency:.2f} Hz")
