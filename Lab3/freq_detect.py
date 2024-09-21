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
    # Check for no signal
    if np.max(samples) - np.min(samples) < 0.1:  # Adjust this threshold as needed
        return "No Signal"

    # Apply the moving average filter to denoise the signal
    filtered_samples = moving_average_filter(samples)

    # Normalize the signal
    normalized_samples = (filtered_samples - np.mean(filtered_samples)) / np.std(
        filtered_samples
    )

    # Calculate statistical measures
    crest_factor = np.max(np.abs(normalized_samples)) / np.sqrt(
        np.mean(normalized_samples**2)
    )
    kurtosis = stats.kurtosis(normalized_samples)

    # Perform FFT for harmonic analysis
    fft_result = np.fft.fft(normalized_samples)
    fft_magnitude = np.abs(fft_result[: len(fft_result) // 2])
    fundamental_freq_index = np.argmax(fft_magnitude[1:]) + 1
    harmonics = fft_magnitude[fundamental_freq_index::fundamental_freq_index]
    harmonic_ratios = harmonics[1:4] / harmonics[0]

    # Decision logic
    if crest_factor > 1.3 and crest_factor < 1.5 and abs(kurtosis) < 0.5:
        return "Sine Wave"
    elif crest_factor < 1.2 and kurtosis > 0 and np.all(harmonic_ratios[::2] > 0.05):
        return "Square Wave"
    else:
        return "Triangle Wave"


def main():
    sample_rate = 2000  # 2000 Hz
    duration = 1  # 1 second
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
    shape = detect_waveform_shape(samples, actual_sample_rate)

    if shape != "No Signal":
        frequency = calculate_frequency(samples, actual_sample_rate)
        print(f"Calculated Frequency: {frequency:.2f} Hz")

    print(f"Detected Waveform Shape: {shape}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        GPIO.cleanup()

