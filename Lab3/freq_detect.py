import numpy as np


# Denoising using a moving average
def denoise_signal(
    signal, window_size=10
):  # Reduced window size for quicker changes in the signal
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def calculate_frequency(data, sampling_rate=1000, threshold=0.05):
    # Denoise the signal
    denoised_data = denoise_signal(data)

    # Detect peaks (local maxima) and valleys (local minima)
    peaks = (np.diff(np.sign(np.diff(denoised_data))) < 0).nonzero()[0] + 1
    valleys = (np.diff(np.sign(np.diff(denoised_data))) > 0).nonzero()[0] + 1

    # Filter out small peaks and valleys (insignificant changes)
    significant_peaks = [
        p for p in peaks if denoised_data[p] > (np.max(denoised_data) * threshold)
    ]
    significant_valleys = [
        v for v in valleys if denoised_data[v] < (np.min(denoised_data) * threshold)
    ]

    # Combine peaks and valleys for full cycle detection
    all_extrema = sorted(np.concatenate((significant_peaks, significant_valleys)))

    # Ensure that we're counting complete cycles
    if len(all_extrema) >= 2:
        # Calculate the period based on the distance between every second extremum
        full_cycle_periods = np.diff(
            all_extrema[::2]
        )  # Every second extremum represents a full cycle

        # Calculate the average period and frequency
        period = np.mean(full_cycle_periods) / sampling_rate
        frequency = 1 / period
        print(f"Detected significant extrema (peaks and valleys): {all_extrema}")
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
