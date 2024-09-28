import board
import busio
import adafruit_mpu6050
from time import sleep, perf_counter
from collections import deque
import math

# Initialize I2C communication and the MPU6050 accelerometer
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# Constants for step detection
step_count = 0
gravity = 9.8  # Approximate gravity in m/s^2
window_size = 5  # Window size for moving average filter
accel_z_buffer = deque(maxlen=window_size)  # Stores last `window_size` z-axis readings
threshold = 1.0  # Dynamic threshold for step detection
min_step_interval = 0.2  # Minimum time between steps in seconds
last_step_time = 0
peak_detected = False


# Function to apply a simple moving average filter
def moving_average(buffer):
    return sum(buffer) / len(buffer)


# Function to remove the gravity component from acceleration
def remove_gravity(accel_x, accel_y, accel_z):
    total_accel = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
    if total_accel > 0:
        gravity_correction_factor = gravity / total_accel
        return (
            accel_x * gravity_correction_factor,
            accel_y * gravity_correction_factor,
            (accel_z - gravity),
        )
    return accel_x, accel_y, accel_z


print("Starting step tracking with gravity removal and filtering...")

while True:
    # Get acceleration data (X, Y, Z)
    accel_x, accel_y, accel_z = mpu.acceleration

    # Remove gravity's effect
    accel_x_corr, accel_y_corr, accel_z_corr = remove_gravity(accel_x, accel_y, accel_z)

    # Add the corrected Z-axis acceleration to the buffer for filtering
    accel_z_buffer.append(accel_z_corr)

    # Apply moving average filter to smooth the Z-axis data
    if len(accel_z_buffer) == window_size:
        filtered_z = moving_average(accel_z_buffer)

        # Get the current time
        current_time = perf_counter()

        # Detect a peak: Z acceleration crosses the threshold, indicating a step
        if (
            not peak_detected
            and abs(filtered_z) > threshold
            and (current_time - last_step_time) > min_step_interval
        ):
            # Step detected
            step_count += 1
            last_step_time = current_time
            peak_detected = True  # Mark peak as detected
            print(f"Step detected! Total steps: {step_count}")

        # Reset peak detection when Z-axis drops below the threshold
        if abs(filtered_z) < threshold / 2:
            peak_detected = False

        # Print current filtered and corrected Z-acceleration for debugging
        print(f"Corrected and Filtered Z Acceleration: {filtered_z:.2f} m/s^2")
        print(f"Total steps: {step_count}")

    # Wait before taking the next measurement
    sleep(0.05)  # Adjust sampling rate for better step detection
