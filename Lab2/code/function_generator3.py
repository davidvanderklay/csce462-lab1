import time
import math
import board
import busio
from adafruit_mcp4725 import MCP4725
import RPi.GPIO as GPIO

# pin for button
BUTTON_PIN = 23

# initialize DAC and I2C
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c)

# button setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def get_user_input():
    while True:
        shape = input("Enter waveform shape (square, triangle, sin): ").strip().lower()
        if shape in ["square", "triangle", "sin"]:
            break
        print("Invalid waveform shape. Please enter 'square', 'triangle', or 'sin'.")

    while True:
        try:
            frequency = float(input("Enter frequency (up to 50 Hz): ").strip())
            if 0 < frequency <= 50:
                break
            else:
                print("Frequency must be greater than 0 and up to 50 Hz.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for frequency.")

    while True:
        try:
            max_voltage = float(input("Enter maximum output voltage (0-5.5V): ").strip())
            if 0 <= max_voltage <= 5.5: 
                break
            else:
                print("Maximum output voltage must be between 0 and 5.5V.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for maximum output voltage.")

    return shape, frequency, max_voltage

def generate_waveform(shape, frequency, max_voltage):
    t = 0.0
    tStep = 1 / (frequency * 100)  # finer time step for smoother waveform
    max_dac_value = 65535  # range for 12 bits
    print("-Generating waveform...")
    time.sleep(1)

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Generate waveform until button is pressed again
            if shape == "square":
                cycle_time = 1 / frequency
                half_cycle = cycle_time / 2
                time_in_cycle = t % cycle_time
                if time_in_cycle < half_cycle:
                    voltage = max_voltage
                else:
                    voltage = 0
                value = int((voltage / 5.5) * max_dac_value)  # scale voltage to DAC value
            elif shape == "triangle":
                cycle_time = 1 / frequency
                time_in_cycle = t % cycle_time
                if time_in_cycle < cycle_time / 2:
                    voltage = (2 * time_in_cycle / cycle_time) * max_voltage
                else:
                    voltage = (2 * (cycle_time - time_in_cycle) / cycle_time) * max_voltage
                value = int((voltage / 5.5) * max_dac_value)
            elif shape == "sin":
                voltage = 0.5 * max_voltage * (1 + math.sin(2 * math.pi * frequency * t))  # proper scaling for sin wave
                value = int((voltage / 5.5) * max_dac_value)
            else:
                print("Invalid waveform shape.")
                return

            # send value to dac
            dac.value = value
            # increment time
            t += tStep
            # wait for next step
            time.sleep(tStep)
        else:
            # Break out of the loop if button is pressed again
            print("-Exiting waveform generation...")
            time.sleep(0.1)
            break

def main():
    while True:
        print("Press the button to start.")
        while GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.01)  # save CPU
        shape, frequency, max_voltage = get_user_input()
        generate_waveform(shape, frequency, max_voltage)
        print("-Exited waveform generation.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        GPIO.cleanup()
