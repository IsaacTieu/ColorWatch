# Run this to start the live webcam footage.
# Adjust the parameter of cv2.VideoCapture() if the script is outputting the wrong camera.
import cv2

# The script in CheckCameras.py finds what number input to cv2.VideoCapture
vid = cv2.VideoCapture(2)

while True:
    bool, frame = vid.read()

    cv2.imshow("Live webcam video", frame)
    cv2.waitKey(1)
    #add potential video saving feature
    #add square on the screen that shows where the color is being calculated
    #my idea is to process each frame, and to take the average of the values of all the pixels
    #in a certain square
    #this gets outputted to a list that is later graphed with matplot
    #this also gets outputted to Excel for data analysis
    #remember that there are outliers here (buffer at the start vs end)
    #write some failsafes for that or maybe add a manual feature for the start and end time
    #i don't like the idea of a manual feature because there is human error
    