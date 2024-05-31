import mpu6050
import time
import math

# Create a new Mpu6050 object
mpu6050 = mpu6050.mpu6050(0x68)

accel_diff = lambda x1, x2, y1, y2, z1, z2 : math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2) + math.pow(z2-z1, 2))

# Define a function to read the sensor data
def read_sensor_data():
    # Read the accelerometer values
    accelerometer_data = mpu6050.get_accel_data()
    return accelerometer_data
    # Read temp
    # temperature = mpu6050.get_temp()

# take new data, compare with last data, return diff
def compare_data(last_accel):
    this_accel = read_sensor_data()
    #print(last_accel)
    diff = accel_diff(last_accel["x"], this_accel["x"], last_accel["y"], this_accel["y"], last_accel["z"], this_accel["z"])
    return this_accel, diff
    
last_accel = read_sensor_data()
time.sleep(0.1)
for i in range(10000):
    last_accel, diff = compare_data(last_accel)
    if diff > 30.0:
        print(diff)
    time.sleep(0.1)

