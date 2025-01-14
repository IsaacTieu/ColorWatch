# The script below checks available webcams for openCV to video capture.
# The numbers it prints out are possibilities for the parameter for the cv2.VideoCapture() function.
# If on a laptop, the parameter '0' refers to the default laptop webcam.
# If the webcam is connected to the USB port on the left side, the parameter is '1'.
# If the webcam is connected to the USB port on the right side, the parameter is '2'.
# The script takes a while to run since VideoCapture is being run multiple times.

import cv2

for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(i)
        cap.release()