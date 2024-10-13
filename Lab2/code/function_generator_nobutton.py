import time
import math
import board
import busio
from adafruit_mcp4725 import MCP4725

# Initialize DAC and I2C
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c)


def get_user_input():
    while True:
        shape = input("Enter waveform shape (square, triangle, sin): ").strip().lower()
        if shape in ["square", "triangle", "sin"]:
            break
        print("Invalid waveform shape. Please enter 'square', 'triangle', or 'sin'.")

    while True:
        try:
            frequency = float(input("Enter frequency (up to 5000 Hz): ").strip())
            if 0 < frequency <= 5000:
                break
            else:
                print("Frequency must be greater than 0 and up to 5000 Hz.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for frequency.")

    while True:
        try:
            max_voltage = float(
                input("Enter maximum output voltage (0-5.5V): ").strip()
            )
            if 0 <= max_voltage <= 5.5:
                break
            else:
                print("Maximum output voltage must be between 0 and 5.5V.")
        except ValueError:
            print(
                "Invalid input. Please enter a numeric value for maximum output voltage."
            )

    return shape, frequency, max_voltage


def generate_waveform(shape, frequency, max_voltage):
    t = 0.0
    points_per_cycle = 1000  # Number of points per cycle for a smooth waveform
    tStep = 1 / (
        frequency * points_per_cycle
    )  # Time step for higher frequency waveforms
    max_dac_value = 65535  # 12-bit DAC range
    print("-Generating waveform...")

    while True:
        if shape == "square":
            cycle_time = 1 / frequency
            half_cycle = cycle_time / 2
            time_in_cycle = t % cycle_time
            if time_in_cycle < half_cycle:
                voltage = max_voltage
            else:
                voltage = 0
            value = int((voltage / 5.5) * max_dac_value)  # Scale voltage to DAC value
        elif shape == "triangle":
            cycle_time = 1 / frequency
            time_in_cycle = t % cycle_time
            if time_in_cycle < cycle_time / 2:
                voltage = (2 * time_in_cycle / cycle_time) * max_voltage
            else:
                voltage = (2 * (cycle_time - time_in_cycle) / cycle_time) * max_voltage
            value = int((voltage / 5.5) * max_dac_value)
        elif shape == "sin":
            voltage = (
                0.5 * max_voltage * (1 + math.sin(2 * math.pi * frequency * t))
            )  # Proper scaling for sine wave
            value = int((voltage / 5.5) * max_dac_value)
        else:
            print("Invalid waveform shape.")
            return

        # Send value to DAC
        dac.value = value
        # Increment time
        t += tStep

        # Remove time.sleep() for higher frequency accuracy
        if frequency > 100:
            # Only add time.sleep for low frequencies where precise timing is less critical
            time.sleep(tStep)


def main():
    while True:
        shape, frequency, max_voltage = get_user_input()
        generate_waveform(shape, frequency, max_voltage)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted")
