# Run this to start the live webcam footage.
# This script may take some time to run (30 seconds - 1 minute) because of the cv2.VideoCapture function. (fixed)
# If there is previous data from a prior run in the current working directory, make sure to move it to another folder.
# This includes '.avi' and '.csv' files.
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import av
import io
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/73609006/how-to-create-a-video-out-of-frames-without-saving-it-to-disk-using-python
# Video capturing code taken from here

# The script in CheckCameras.py finds what possible numbers to input to cv2.VideoCapture.
# Adjust 'camera' if the script is outputting the wrong camera.
# This is very finicky since openCV doesn't give information about what number correlates to what camera.
# There will be a lot of trial and error figuring out the right camera, because the number can hop around.
camera = 0
warning_sign_length = 90

print("Hold down your mouse and move it to select the region of interest")
print("Press 'q' once finished to move on. Make sure NUMLOCK is locking the number pad.")

vid = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
fps = int(vid.get(cv2.CAP_PROP_FPS))
width  = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
color = (0, 0, 0)
thickness = 3

start = None
end = None
drawing = False

# This detects mouse movements/inputs for the region of interest (ROI).
def draw_rectangle(event, x, y, flags, param):
    global start, end, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end = (x, y)

cv2.namedWindow("rectangle")
cv2.setMouseCallback("rectangle", draw_rectangle)

# This is the loop where the ROI is drawn.
while True:
    _, image = vid.read()

    if start and end:
        image = cv2.rectangle(image, start, end, color, thickness)

    cv2.imshow("rectangle", image)

    # Press the video window and then 'q' to quit and move on.
    # MAKE SURE NUMLOCK IS TURNED ON (can't press the number keys)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()

print("If you don't want to detect a certain value, then type '256' because that is higher than the max difference.")

# Once the ROI is set, users are asked to input the RGB color changes to detect.
red_ui = input("Enter the RED value change to detect as an integer: ")
green_ui = input("Enter the GREEN value change to detect as an integer: ")
blue_ui = input("Enter the BLUE value change to detect as an integer: ")

user_inputs = [red_ui, green_ui, blue_ui]

print("Once done taking measurements, press 'q' to save and export the data.")

vid = cv2.VideoCapture(camera, cv2.CAP_DSHOW)

colors = []
color_change_data = []
colors_per_second = []
notes = []

frame_counter = 0
warning_counter = 0
prev_color = None
warning = False
font = cv2.FONT_HERSHEY_SIMPLEX

output_memory_file = io.BytesIO()
output = av.open(output_memory_file, 'w', format="mp4")
stream = output.add_stream('h264', fps)
stream.width = width
stream.height = height
stream.pix_fmt = 'yuv420p'
stream.options = {'crf': '17'}  # Lower crf = better quality & more file space.

fig, ax = plt.subplots(1, 3, figsize=(9, 3))
x_data = []
red_plot = []
green_plot = []
blue_plot = []
x_axis_counter = 0

while True:
    _, frame = vid.read()




    # This section detects change in color based on user input and displays a warning sign.
    if frame_counter == 1:
        prev_color = colors[-1]
    # The warning sign will be on for 90 frames (3 seconds).
    if warning_counter == warning_sign_length:
        warning = False
    # Checks for color change every 31st frame (approximately every second) and then resets.
    if frame_counter == 31:
        frame_counter = 0
        test_color = colors[-1]
        color_diff = [abs(x - y) for x, y in zip(test_color, prev_color)] #[B, G, R]
        for i in range(len(color_diff)):
            if int(color_diff[i]) > int(user_inputs[i]):
                warning = True
                warning_counter = 0
                current_time = datetime.datetime.now()
                data = (current_time, color_diff[0], color_diff[1], color_diff[2],
                                          len(colors) + 1, len(colors_per_second) + 1, i)
                color_change_data.append(data)
                break

    # If a color change is detected, a warning message is displayed.
    if warning:
        text = 'COLOR CHANGE DETECTED'
        (text_width, text_height), _ = cv2.getTextSize(text, font, 1, 3)
        x = (width - text_width) // 2
        y = height // 8 + text_height // 2
        frame = cv2.putText(frame, text, (x, y), font, 1,
                            (255, 0, 0), 3)

    # start and end are determined from the original ROI changer.
    frame = cv2.rectangle(frame, start, end, color, thickness)

    # This finds the average of all the pixel values in the square for one frame
    reds = []
    greens = []
    blues = []

    for r in range(start[1] + thickness, end[1] - thickness):
        for c in range(start[0] + thickness, end[0] - thickness):
            pixel = frame[r][c] # List of the 3 RGB values as [B, G, R]
            blues.append(pixel[0])
            greens.append(pixel[1])
            reds.append(pixel[2])

    average_red = np.mean(reds)
    average_green = np.mean(greens)
    average_blue = np.mean(blues)

    frame_average_color = [average_red, average_green, average_blue]
    colors.append(frame_average_color)

    frame_counter += 1
    if warning_counter < warning_sign_length:
        warning_counter += 1

    if frame_counter == 30:
        colors_per_second.append(frame_average_color)

    image = av.VideoFrame.from_ndarray(frame, format='bgr24')
    packet = stream.encode(image)
    output.mux(packet)  # Write the encoded frame to MP4 file.

    x_data.append(x_axis_counter)
    x_axis_counter += 1
    red_plot.append(frame_average_color[0])
    green_plot.append(frame_average_color[1])
    blue_plot.append(frame_average_color[2])

    ax[0].clear()
    ax[1].clear()
    ax[2].clear()

    ax[0].plot(x_data, red_plot, color='r', label='Red')
    ax[1].plot(x_data, green_plot, color='g', label='Green')
    ax[2].plot(x_data, blue_plot, color='b', label='Blue')

    ax[0].legend()
    ax[1].legend()
    ax[2].legend()

    plt.draw()
    plt.pause(0.01)

    cv2.imshow("Live webcam video", frame)
    plt.show(block=False)


    # Press the video window and then 'q' to quit and export the color data
    # MAKE SURE NUMLOCK IS TURNED ON (can't press the number keys)
    key = cv2.waitKey(1)
    if key == ord('u'):
        note = input('Type a note')
        notes.append([note, len(colors) + 1, len(colors_per_second)])
    if key & 0xFF == ord('q'):
        break

vid.release()
packet = stream.encode(None)
output.mux(packet)
output.close()
cv2.destroyAllWindows()

with open("output.mp4", "wb") as f:
    f.write(output_memory_file.getbuffer())


color_df = pd.DataFrame(colors, columns=['Red', 'Green', 'Blue'])
colors_per_second_df = pd.DataFrame(colors_per_second, columns=['Red', 'Green', 'Blue'])
color_change_df = pd.DataFrame(color_change_data, columns=['Current time: Date / HH:MM:SS',
                                                           'Red Difference',
                                                           'Green Difference',
                                                           'Blue Difference',
                                                           'Color Table Row Number',
                                                           'Colors per Second Table Row Number',
                                                           'Color Detected (blue=0, green=1, red=2)'])
notes_df = pd.DataFrame(notes, columns=['Note', 'Color Table Row Number',
                                        'Colors per Second Table Row  Number'])


def file_check(file_path, dataframe, file_name):
    if os.path.exists(file_path):
        first_yes = input(f"Enter 'yes' to continue after you have moved '{file_path}' to another folder. "
                    f"If not moved, the current file will be overwritten. \n"
                    f"If something else is entered, the old file will stay and the current file will be lost: ")
        possible_inputs = ['yes', ' yes', 'yes ', 'YES', ' YES', 'YES ', "'yes'", "'Yes'"]
        if first_yes in possible_inputs:
            try:
                dataframe.to_csv(file_name, mode='w', index=False)
            except PermissionError:
                error_input = input("There is a permission error happening. Try closing the excel."
                                    "Type 'yes' once done.")
                if error_input in possible_inputs:
                    dataframe.to_csv(file_name, mode='w', index=False)
        else:
            second_yes = input('Last chance to save the file. Type "yes" to save the file ')
            if second_yes in possible_inputs:
                try:
                    dataframe.to_csv(file_name, mode='w', index=False)
                except PermissionError:
                    error_input = input("There is a permission error happening. Try closing the excel."
                                        "Type 'yes' once done.")
                    if error_input in possible_inputs:
                        dataframe.to_csv(file_name, mode='w', index=False)
    else:
        dataframe.to_csv(file_name, mode='w', index=False)




# This webcam is 30 FPS, which means that each second gives 30 rows of color data
# Can rename 'colorData'. This is the table of all the RGB values throughout the reaction.
file_check('colorData.csv', color_df, 'colorData.csv')

# Can rename 'colorsPerSecondData'. This is the table of the RGB values at each second to shorten Excel.
file_check('colorsPerSecondData.csv', colors_per_second_df, 'colorsPerSecondData.csv')

# Can rename 'colorChangeData'. This is the data for when a color change is detected.
file_check('colorChangeData.csv', color_change_df, 'colorChangeData.csv')

file_check('notes.csv', notes_df, 'notes.csv')

# All of these files are saved into the current working directory (CWD).
# Make sure to transfer the data files somewhere else if it needs to be referenced later.

















# 1/14
# add failsafe for video saving
# add failsafe for ROI and RGB change detection overlap
# Eventually add type in coordinates feature? Note that the top left is (0,0)
# Add way to live show data
# Add way to add notes about what is happening







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
    # I need to experiment and have an idea of what constitutes a worthy color change
    #Potential functionality for dividing input changes into red/green/blues values


# half_length = width // 6
# start = (width // 2 - half_length, height // 2 - half_length)
# end = (width // 2 + half_length, height // 2 + half_length)
# start = (214, 134); end = (426, 346)


#'rxn.avi' can be renamed. This is the video of the reaction that will be saved.
#codec = cv2.VideoWriter_fourcc(*'XVID')

#out = cv2.VideoWriter('rx.avi', codec, fps, (width, height))
#out.write(frame)
#out.release()

#os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

