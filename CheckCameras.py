# The script below checks available webcams for openCV to video capture.
# The numbers it prints out are possibilities for the parameter for the cv2.VideoCapture() function.
# If on a laptop, the parameter '0' refers to the default laptop webcam.
# If the webcam is connected to USB port on the right side, the parameter is '2'.
# The script takes a while to run since VideoCapture is being run multiple times.

import cv2
device_list = []
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        device_list.append(f"Device {i}")
        cap.release()

for i in range(len(device_list)):
    print(f"Possible Video Capture parameter: {i}")