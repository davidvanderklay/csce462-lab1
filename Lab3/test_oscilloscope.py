import numpy as np
import matplotlib.pyplot as plt


def detect_waveform_shape(data):
    max_val = np.max(data)
    min_val = np.min(data)
    amplitude = max_val - min_val

    if amplitude == 0:
        return "Unknown Waveform (Flat Line)"

    normalized_data = (data - min_val) / amplitude

    # Check for Sine Wave
    first_diff = np.diff(normalized_data)
    second_diff = np.diff(first_diff)

    # Smoothness check
    is_smooth = np.all(np.abs(second_diff) < 0.005)  # Tighter threshold for smoothness

    # Debugging output
    print(f"Amplitude: {amplitude}")
    print(
        f"Normalized Data Range: {np.min(normalized_data)} to {np.max(normalized_data)}"
    )
    print(f"Smoothness Check: {is_smooth}")

    if is_smooth:
        return "Sine Wave"

    # Check for Square Wave
    threshold = 0.85
    high_vals = normalized_data > threshold
    low_vals = normalized_data < (1 - threshold)

    if np.mean(high_vals) > 0.45 and np.mean(low_vals) > 0.45:
        return "Square Wave"

    # Check for Triangle Wave
    rising_slope = np.mean(first_diff[: len(first_diff) // 2])
    falling_slope = np.mean(first_diff[len(first_diff) // 2 :])

    # Adjusted conditions for triangle wave detection
    if np.abs(rising_slope) < 0.2 and np.abs(falling_slope) < 0.2:
        return "Triangle Wave"

    return "Unknown Waveform"


def generate_sine_wave(frequency, sampling_rate, duration):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t), t


def generate_square_wave(frequency, sampling_rate, duration):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    return np.sign(np.sin(2 * np.pi * frequency * t)), t


def generate_triangle_wave(frequency, sampling_rate, duration):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    return 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1, t


def add_noise(signal, noise_level=0.05):
    noise = np.random.normal(0, noise_level, signal.shape)
    return signal + noise


# Denoising using a moving average
def denoise_signal(signal, window_size=50):
    return np.convolve(signal, np.ones(window_size) / window_size, mode="same")


def plot_waveform(t, data, title):
    plt.figure(figsize=(8, 4))
    plt.plot(t, data)
    plt.title(title)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()


def test_waveform_detection():
    sampling_rate = 1000000  # Samples per second
    duration = 1  # 1 second duration for each wave

    frequencies = [1, 5, 10, 20]  # Test for different frequencies

    for freq in frequencies:
        print(f"Testing frequency: {freq} Hz")

        # Test Sine Wave
        sine_wave, t = generate_sine_wave(freq, sampling_rate, duration)
        noisy_sine_wave = add_noise(sine_wave)
        denoised_sine_wave = denoise_signal(noisy_sine_wave)
        plot_waveform(t, denoised_sine_wave, f"Denoised Sine Wave - {freq} Hz")
        result = detect_waveform_shape(denoised_sine_wave)
        print(f"Sine Wave: Detected as {result}")

        # Test Square Wave
        square_wave, t = generate_square_wave(freq, sampling_rate, duration)
        noisy_square_wave = add_noise(square_wave)
        denoised_square_wave = denoise_signal(noisy_square_wave)
        plot_waveform(t, denoised_square_wave, f"Denoised Square Wave - {freq} Hz")
        result = detect_waveform_shape(denoised_square_wave)
        print(f"Square Wave: Detected as {result}")

        # Test Triangle Wave
        triangle_wave, t = generate_triangle_wave(freq, sampling_rate, duration)
        noisy_triangle_wave = add_noise(triangle_wave)
        denoised_triangle_wave = denoise_signal(noisy_triangle_wave)
        plot_waveform(t, denoised_triangle_wave, f"Denoised Triangle Wave - {freq} Hz")
        result = detect_waveform_shape(denoised_triangle_wave)
        print(f"Triangle Wave: Detected as {result}")
        print("-" * 50)


if __name__ == "__main__":
    test_waveform_detection()
