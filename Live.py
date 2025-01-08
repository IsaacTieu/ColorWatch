# Run this to start the live webcam footage.
# Adjust the parameter of cv2.VideoCapture() if the script is outputting the wrong camera.
import cv2
import numpy as np
import pandas as pd

user_input = input("Enter a rapid RGB value change as an integer: ")

# The script in CheckCameras.py finds what possible numbers to input to cv2.VideoCapture
vid = cv2.VideoCapture(1)
codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

fps = vid.get(cv2.CAP_PROP_FPS)
width  = vid.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float
width = int(width)
height = int(height)

colors = []

frame_counter = 0
prev_color = None
warning = False
warning_counter = 0
font = cv2.FONT_HERSHEY_SIMPLEX

# 'rxn.avi' can be renamed
#out = cv2.VideoWriter('rxn.avi', codec, fps, (int(width), int(height)))

while True:
    bool, frame = vid.read()

    if frame_counter == 1:
        prev_color = colors[-1]
    if warning_counter == 90:
        warning = False
    if frame_counter == 31:
        frame_counter = 0
        test_color = colors[-1]
        color_diff = [abs(x - y) for x, y in zip(test_color, prev_color)]
        #user input for color change = _
        for num in color_diff:
            if int(num) >= int(user_input):
                warning = True
                warning_counter = 0


    print(warning)
    if warning == True:
        frame = cv2.putText(frame, 'RAPID COLOR CHANGE DETECTED',
                            (width // 2 - width // 6, height // 2 - height // 6), font, 2,
                            (255, 0, 0), 3)





    # Properties of the square on the image
    # start is the top left corner coordinates
    # end is the bottom right corner coordinates
    # (0, 0) is the top left of the image

    half_length = width // 6
    start = (width // 2 - half_length, height // 2 - half_length)
    end = (width // 2 + half_length, height // 2 + half_length)
    color = (0, 0, 0)
    thickness = 3

    frame = cv2.rectangle(frame, start, end, color, thickness)

    # Finds the average of all the pixel values in the square for one frame

    top_left = start
    top_right = (end[0], start[1])
    bottom_left = (start[0], end[1])
    bottom_right = end

    reds = []
    greens = []
    blues = []
    #print(frame[start[0] + 50][end[0] + 50])

    # print(start[0] + thickness)
    # print(end[1] - start[1])
    # print(start[1] + thickness)
    # print(end[0] - start[0])
    # print("STOPTOPTOPTOPTOPTOTPOT")


    #need to double check if these are the correct ranges!!!
    for r in range(start[1] + thickness, end[1] - start[1]):
        for c in range(start[1] + thickness, end[0] - start[0]):
            pixel = frame[r][c] # List of the 3 RGB values
            reds.append(pixel[0])
            greens.append(pixel[1])
            blues.append(pixel[2])


    average_red = np.mean(reds)
    average_green = np.mean(greens)
    average_blue = np.mean(blues)

    frame_average_color = [average_red, average_green, average_blue]
    colors.append(frame_average_color)

    frame_counter += 1
    warning_counter += 1

    cv2.imshow("Live webcam video", frame)

    # Press the video and then 'q' to quit and export the color data
    cv2.waitKey(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# vid.release()
# out.release()
cv2.destroyAllWindows()

df = pd.DataFrame(colors, columns=['Red', 'Green', 'Blue'])

# Can rename 'colorData'
# This webcam is 30 FPS, which means that each second gives 30 rows of color data
df.to_csv('colorData.csv', index=False)












    #add potential video saving feature
    #add square on the screen that shows where the color is being calculated
    #my idea is to process each frame, and to take the average of the values of all the pixels
    #in a certain square
    #this gets outputted to a list that is later graphed with matplot
    #this also gets outputted to Excel for data analysis
    #remember that there are outliers here (buffer at the start vs end)
    #write some failsafes for that or maybe add a manual feature for the start and end time
    #i don't like the idea of a manual feature because there is human error
    #monitor for spike in color change
    # remove noise
    #user defined threshold when the rate of change is at a certain amount
    # alert on webcam
    #clock time for rapid color change
