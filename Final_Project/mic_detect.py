import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import wave
import numpy as np

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
# Create the CS (chip select)
cs = digitalio.DigitalInOut(board.D5)
# Create the MCP object
mcp = MCP.MCP3008(spi, cs)
# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)


def voltage_to_pcm(voltage, max_voltage=3.3):
    """Convert a voltage reading to a PCM value."""
    max_pcm_value = 32767  # 16-bit audio format
    scaled_value = int((voltage / max_voltage) * max_pcm_value)  # Convert to int
    return np.clip(scaled_value, -max_pcm_value, max_pcm_value)


def main():
    sample_rate = 500  # 44.1 kHz sample rate, standard for audio files
    duration = 5  # Record for 5 seconds
    num_samples = int(sample_rate * duration)
    output_file = "microphone_output.wav"  # Output audio file

    try:
        # Open the WAV file for writing
        with wave.open(output_file, "w") as wf:
            # Set the parameters for the WAV file (1 channel, 16 bits per sample, 44.1 kHz sample rate)
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
            wf.setframerate(sample_rate)

            print(f"Recording {duration} seconds of audio...")

            start_time = time.time()

            for _ in range(num_samples):
                voltage = chan.voltage  # Read voltage from MCP3008
                pcm_value = voltage_to_pcm(voltage)  # Convert voltage to PCM
                # Convert pcm_value to a standard Python integer before writing
                wf.writeframes(
                    int(pcm_value).to_bytes(2, byteorder="little", signed=True)
                )  # Write PCM data to WAV

                # Sleep to maintain consistent sampling rate
                time.sleep(1 / sample_rate)

            actual_sample_rate = num_samples / (time.time() - start_time)
            print(
                f"Recording complete. Actual sample rate: {actual_sample_rate:.2f} Hz"
            )
            print(f"Audio saved to {output_file}")

    except KeyboardInterrupt:
        print("\nExiting program.")


if __name__ == "__main__":
    main()
