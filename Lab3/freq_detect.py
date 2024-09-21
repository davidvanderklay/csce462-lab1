import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import RPi.GPIO as GPIO
import numpy as np
from scipy import stats

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D5)
# Create the MCP object
mcp = MCP.MCP3008(spi, cs)
# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)


def calculate_frequency(samples, sample_rate):
    zero_crossings = np.where(np.diff(np.sign(samples - np.mean(samples))))[0]
    frequency = len(zero_crossings) * sample_rate / (2 * len(samples))
    return frequency


def moving_average_filter(samples, window_size=5):
    return np.convolve(samples, np.ones(window_size) / window_size, mode="valid")


def detect_waveform_shape(samples, sample_rate):
    # Apply the moving average filter to denoise the signal
    filtered_samples = moving_average_filter(samples)

    # Normalize the signal
    normalized_samples = (filtered_samples - np.mean(filtered_samples)) / np.std(
        filtered_samples
    )

    # Perform FFT
    fft_result = np.fft.fft(normalized_samples)
    fft_freq = np.fft.fftfreq(len(normalized_samples), 1 / sample_rate)
    positive_freqs = fft_freq[: len(fft_freq) // 2]
    positive_fft_result = np.abs(fft_result[: len(fft_result) // 2]) / len(
        normalized_samples
    )

    # Find the fundamental frequency
    fundamental_freq_index = (
        np.argmax(positive_fft_result[1:]) + 1
    )  # Ignore DC component
    fundamental_freq = positive_freqs[fundamental_freq_index]

    # Calculate statistical measures
    crest_factor = np.max(np.abs(normalized_samples)) / np.sqrt(
        np.mean(normalized_samples**2)
    )
    kurtosis = stats.kurtosis(normalized_samples)

    # Calculate derivatives
    first_derivative = np.diff(normalized_samples)
    second_derivative = np.diff(first_derivative)

    # Decision logic
    if (
        np.max(positive_fft_result[fundamental_freq_index::2])
        > 0.1 * positive_fft_result[fundamental_freq_index]
        and crest_factor < 1.2
    ):
        return "Square Wave"
    elif crest_factor > 1.3 and crest_factor < 1.5 and kurtosis < -1:
        return "Sine Wave"
    else:
        return "Triangle Wave"


def main():
    sample_rate = 2000  # Increased to 2000 Hz
    duration = 1  # Reduced to 1 second for faster processing
    num_samples = sample_rate * duration
    samples = []

    print("Collecting samples...")
    start_time = time.time()
    for _ in range(num_samples):
        voltage = chan.voltage
        samples.append(voltage)

    actual_sample_rate = num_samples / (time.time() - start_time)
    print(f"Actual sample rate: {actual_sample_rate:.2f} Hz")

    samples = np.array(samples)
    frequency = calculate_frequency(samples, actual_sample_rate)
    shape = detect_waveform_shape(samples, actual_sample_rate)

    print(f"Calculated Frequency: {frequency:.2f} Hz")
    print(f"Detected Waveform Shape: {shape}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        GPIO.cleanup()

