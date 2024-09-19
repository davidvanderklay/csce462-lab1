import numpy as np
import matplotlib.pyplot as plt


def detect_waveform_shape(data):
    max_val = np.max(data)
    min_val = np.min(data)
    amplitude = max_val - min_val

    if amplitude == 0:
        return "Unknown Waveform (Flat Line)"

    normalized_data = (data - min_val) / amplitude

    # Check for Square Wave
    threshold = 0.9
    high_vals = normalized_data > threshold
    low_vals = normalized_data < (1 - threshold)

    if np.mean(high_vals) > 0.45 and np.mean(low_vals) > 0.45:
        return "Square Wave"

    # Check for Triangle Wave
    diffs = np.diff(normalized_data)
    rising = diffs[: len(diffs) // 2]
    falling = diffs[len(diffs) // 2 :]

    is_linear_rise = np.all(np.abs(np.diff(rising)) < 0.05)  # Adjusted tolerance
    is_linear_fall = np.all(np.abs(np.diff(falling)) < 0.05)  # Adjusted tolerance

    if is_linear_rise and is_linear_fall:
        return "Triangle Wave"

    # Check for Sine Wave
    first_diff = np.diff(normalized_data)
    second_diff = np.diff(first_diff)

    is_smooth = np.all(np.abs(second_diff) < 0.02)  # Adjusted smoothness
    is_not_linear = np.std(first_diff) > 0.01

    fft_result = np.fft.fft(normalized_data)

    is_sine_wave = np.abs(fft_result[1]) > (
        np.abs(fft_result[2]) + np.abs(fft_result[3])
    )

    if is_smooth and is_not_linear and is_sine_wave:
        return "Sine Wave"

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


def add_noise(signal, noise_level=0.1):
    noise = np.random.normal(0, noise_level, signal.shape)  # Gaussian noise
    return signal + noise


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
        plot_waveform(t, noisy_sine_wave, f"Noisy Sine Wave - {freq} Hz")
        result = detect_waveform_shape(noisy_sine_wave)
        print(f"Sine Wave: Detected as {result}")

        # Test Square Wave
        square_wave, t = generate_square_wave(freq, sampling_rate, duration)
        noisy_square_wave = add_noise(square_wave)
        plot_waveform(t, noisy_square_wave, f"Noisy Square Wave - {freq} Hz")
        result = detect_waveform_shape(noisy_square_wave)
        print(f"Square Wave: Detected as {result}")

        # Test Triangle Wave
        triangle_wave, t = generate_triangle_wave(freq, sampling_rate, duration)
        noisy_triangle_wave = add_noise(triangle_wave)
        plot_waveform(t, noisy_triangle_wave, f"Noisy Triangle Wave - {freq} Hz")
        result = detect_waveform_shape(noisy_triangle_wave)
        print(f"Triangle Wave: Detected as {result}")
        print("-" * 50)


if __name__ == "__main__":
    test_waveform_detection()
