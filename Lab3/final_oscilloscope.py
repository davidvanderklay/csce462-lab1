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
    if np.max(samples) < 0.1:
        return "No Voltage"

    filtered_samples = moving_average_filter(samples)
    normalized_samples = (filtered_samples - np.mean(filtered_samples)) / np.std(
        filtered_samples
    )

    fft_result = np.fft.fft(normalized_samples)
    positive_fft_result = np.abs(fft_result[: len(fft_result) // 2]) / len(
        normalized_samples
    )

    fundamental_freq_index = np.argmax(positive_fft_result[1:]) + 1

    crest_factor = np.max(np.abs(normalized_samples)) / np.sqrt(
        np.mean(normalized_samples**2)
    )
    kurtosis = stats.kurtosis(normalized_samples)

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
    sample_rate = 2000  # 2000 Hz
    duration = 0.5  # 0.5 seconds for faster updates
    num_samples = int(sample_rate * duration)

    last_shape = None
    last_frequency = None

    try:
        while True:
            samples = []
            start_time = time.time()

            for _ in range(num_samples):
                voltage = chan.voltage
                samples.append(voltage)

            actual_sample_rate = num_samples / (time.time() - start_time)
            samples = np.array(samples)

            shape = detect_waveform_shape(samples, actual_sample_rate)

            if shape != "No Voltage":
                frequency = calculate_frequency(samples, actual_sample_rate)

                # Check for significant changes
                if (
                    (shape != last_shape)
                    or (last_frequency is None)
                    or (abs(frequency - last_frequency) > 1)
                ):
                    print(f"Detected Waveform Shape: {shape}")
                    print(f"Calculated Frequency: {frequency:.2f} Hz")
                    print(f"Actual sample rate: {actual_sample_rate:.2f} Hz")
                    print("---")

                    last_shape = shape
                    last_frequency = frequency

            elif shape != last_shape:
                print("No Voltage detected")
                print("---")
                last_shape = shape
                last_frequency = None

            time.sleep(0.1)  # Short delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()

