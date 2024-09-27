import board
import busio
import adafruit_mpu6050
from time import sleep, perf_counter

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

step_count = 0
threshold = 8  # threshold for step detection
last_z_accel = 0
step_interval = 0.3  # minimum time between to avoid false detection
last_step_time = 0

print("Starting step tracking...")

while True:
    # yoink data
    accel_x, accel_y, accel_z = mpu.acceleration

    # get time
    current_time = perf_counter()

    # check when acceleration passes a threshold
    if abs(accel_z) > threshold and (current_time - last_step_time) > step_interval:
        step_count += 1
        last_step_time = current_time
        print(f"Step detected! Total steps: {step_count}")
    #
    # # print info to debug
    # print(f"Acceleration: X: {accel_x:.2f}, Y: {accel_y:.2f}, Z: {accel_z:.2f} m/s^2")
    # print(f"Total steps: {step_count}")
    #
    # delay between measurements
    sleep(0.1)
