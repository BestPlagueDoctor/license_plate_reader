from datetime import datetime
import subprocess
import numpy as np
import mpu6050
import cv2
import time
import math

# cheap square distance lambda
accel_diff = lambda x1, x2, y1, y2, z1, z2 : math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2) + math.pow(z2-z1, 2))

# read the sensors
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

# Create a new Mpu6050 object
mpu6050 = mpu6050.mpu6050(0x68)

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')

w, h = cap.get(3), cap.get(4)
fps = cap.get(5) # fps

len_clip = 60
num_frames = fps*len_clip

i=0
frameList = []
crashed = False
last_accel = read_sensor_data()
while(True):
    try:
        ret, frame = cap.read()
        frameList.append(frame)

        if(len(frameList) > num_frames):
            frameList.pop(0)

        last_accel, diff = compare_data(last_accel)
        if diff > 5.0:
            print(diff)
        if diff > 10.0:
            crashed = True
            print(diff)
        if(crashed == True):
            now = datetime.now()
            outfile = now.strftime("%Y%m%d_%H%M%S") + ".avi"
            out = cv2.VideoWriter(outfile, fourcc, 30.0, (640, 480))
            for frame in frameList:
                out.write(frame)
            # let the video finish writing
            time.sleep(10)
            subprocess.Popen(["rsync", "-e", "'-p 479'", "-auvzhP", "--include==*.avi", "--exclude=*.py", ".", "sam@67.173.100.107:~/479/project/"])
            crashed = False
            
    except OSError as e:
        print(e)
            

# When everything done, release the capture
cap.release()
out.release()
cv2.destroyAllWindows()
