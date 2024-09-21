import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO
import numpy as np

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D5)

# Create the MCP object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)


def calculate_frequency(samples, sample_rate):
    zero_crossings = 0
    previous_sample = samples[0]

    for sample in samples[1:]:
        if previous_sample < 1.65 and sample >= 1.65:  # Adjust for centering at 1.65V
            zero_crossings += 1
        previous_sample = sample

    frequency = (zero_crossings / 2) * (sample_rate / len(samples))
    return frequency


def moving_average_filter(samples, window_size=5):
    """Applies a moving average filter to smooth the signal."""
    return np.convolve(samples, np.ones(window_size) / window_size, mode="same")


def detect_waveform_shape_fft(samples, sample_rate):
    # Apply the moving average filter to denoise the signal
    filtered_samples = moving_average_filter(samples)

    # Perform FFT on the filtered signal
    fft_result = np.fft.fft(filtered_samples)
    fft_freq = np.fft.fftfreq(len(filtered_samples), 1 / sample_rate)

    # Consider only the positive frequencies (ignore negative part of FFT)
    positive_freqs = fft_freq[: len(fft_freq) // 2]
    positive_fft_result = np.abs(fft_result[: len(fft_result) // 2])

    # Find the fundamental frequency (the highest peak in the FFT)
    fundamental_freq_index = np.argmax(positive_fft_result)
    fundamental_freq = positive_freqs[fundamental_freq_index]

    print(f"Fundamental Frequency: {fundamental_freq:.2f} Hz")

    # Analyze harmonic content to classify waveform
    harmonic_peaks = positive_fft_result[fundamental_freq_index::2]  # Odd harmonics
    harmonic_strengths = harmonic_peaks[:5]  # Look at first 5 harmonics

    print(f"Harmonic Strengths: {harmonic_strengths}")

    # Classification based on harmonic content
    if np.all(harmonic_strengths < 0.1 * positive_fft_result[fundamental_freq_index]):
        return "Sine Wave"
    elif np.any(harmonic_strengths > 0.1 * positive_fft_result[fundamental_freq_index]):
        return (
            "Square Wave"
            if harmonic_strengths[1] > harmonic_strengths[2]
            else "Triangle Wave"
        )

    return "Unknown Waveform"


def main():
    sample_rate = 1000  # Samples per second
    duration = 5  # Duration in seconds
    num_samples = sample_rate * duration

    samples = []

    print("Collecting samples...")
    for _ in range(num_samples):
        voltage = chan.voltage  # Read the voltage
        samples.append(voltage)  # Store the voltage value
        time.sleep(1.0 / sample_rate)

    frequency = calculate_frequency(samples, sample_rate)
    shape = detect_waveform_shape_fft(np.array(samples), sample_rate)

    print(f"Calculated Frequency: {frequency:.2f} Hz")
    print(f"Detected Waveform Shape: {shape}")

    # Cleanup
    GPIO.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
        GPIO.cleanup()
