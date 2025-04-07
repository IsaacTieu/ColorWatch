import cv2


def check_cameras():
    """
    Checks available webcams for open CV to video capture. There is a lot of variability, but typically, the guidelines below run true.
    
    If on a laptop, the parameter '0' refers to the default laptop webcam.
    If the webcam is connected to the USB port on the left side, the parameter is '1'.
    If the webcam is connected to the USB port on the right side, the parameter is '2'.

    Output:
        Prints out possible camera_index numbers
    """
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(i)
            cap.release()