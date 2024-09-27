import board
import busio
import adafruit_mpu6050
from time import sleep, perf_counter
from collections import deque

# Initialize I2C communication and the MPU6050 accelerometer
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

# Variables for step detection
step_count = 0
window_size = 5  # Window size for moving average filter
accel_z_buffer = deque(maxlen=window_size)  # Stores last `window_size` z-axis readings
threshold = 1.5  # Dynamic threshold, tuned for noise filtering
min_step_interval = 0.1  # Minimum time between steps for running (in seconds)
last_step_time = 0
peak_detected = False


# Function to apply a simple moving average filter
def moving_average(buffer):
    return sum(buffer) / len(buffer)


print("Starting step tracking with filtering...")

while True:
    # Get acceleration data (X, Y, Z)
    accel_x, accel_y, accel_z = mpu.acceleration

    # Add the Z-axis acceleration to the buffer for filtering
    accel_z_buffer.append(accel_z)

    # Apply moving average filter to smooth the Z-axis data
    if len(accel_z_buffer) == window_size:
        filtered_z = moving_average(accel_z_buffer)

        # Get the current time
        current_time = perf_counter()

        # Detect a peak: crossing the threshold in positive or negative direction
        if (
            not peak_detected
            and filtered_z > threshold
            and (current_time - last_step_time) > min_step_interval
        ):
            # Step detected
            step_count += 1
            last_step_time = current_time
            peak_detected = True  # Mark peak as detected
            print(f"Step detected! Total steps: {step_count}")

        # Reset peak detection after Z-axis drops below the threshold
        if filtered_z < threshold / 2:
            peak_detected = False

        # Print current filtered Z-acceleration for debugging
        print(f"Filtered Z Acceleration: {filtered_z:.2f} m/s^2")
        print(f"Total steps: {step_count}")

    # Wait before taking the next measurement
    sleep(0.05)  # Adjust to get more frequent readings for quicker step detection
