import datetime
import av
import io
import cv2
import threading
import time
import pymsteams
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

font = cv2.FONT_HERSHEY_SIMPLEX
rectangle_color = (0, 0, 0)
thickness = 3
webhook_url = None
start = end = None
camera_index = warning_sign_length = color_detection_time = None
red_value = blue_value = green_value = None
color_df = colors_per_second_df = color_change_df = None
output_memory_file = io.BytesIO()

fig, ax = plt.subplots(1, 3, figsize=(6, 2))
x_data = []
red_plot = []
green_plot = []
blue_plot = []

def define_roi(camera_index):
    # Camera dimensions
    vid = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    drawing = False

    # This detects mouse movements/inputs for the region of interest (ROI).
    def draw_rectangle(event, x, y, flags, param):
        global start, end
        nonlocal drawing

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
            image = cv2.rectangle(image, start, end, rectangle_color, thickness)

        cv2.imshow("rectangle", image)

        # Press the video window and then 'q' to quit and move on.
        # MAKE SURE NUMLOCK IS TURNED ON (number pad is locked)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()

    if not start and not end:
        raise ValueError('No Region of Interest input')

def live_monitoring(camera_index):
    global start, end, rectangle_color, thickness, color_df, colors_per_second_df, color_change_df, output_memory_file
    user_inputs = [red_value, green_value, blue_value]
    vid = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Output data
    colors = []
    color_change_data = []
    colors_per_second = []
    # notes = []

    # Internal counters
    frame_counter = 0
    warning_counter = 0
    prev_color = None
    warning = False

    # Video saving feature
    output = av.open(output_memory_file, 'w', format="mp4")
    stream = output.add_stream('h264', fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': '17'}  # Lower crf = better quality & more file space.

    rxn_start_time = time.time()
    start_time = time.time()

    while True:
        success, frame = vid.read()
        if not success:
            continue

        end_time = time.time()
        time_diff = end_time - start_time

        # This section detects change in color based on user input and displays a warning sign.
        if frame_counter == 1:
            prev_color = colors[-1]
        # The warning sign will be on for warning_sign_length (frames).
        if warning_counter == warning_sign_length:
            warning = False
        # Checks for color change every color_detection_time seconds.
        if time_diff >= color_detection_time:
            start_time = end_time
            frame_counter = 0
            test_color = colors[-1]
            color_diff = [abs(x - y) for x, y in zip(test_color, prev_color)]  # [B, G, R]
            for i in range(len(color_diff) - 1):  # The -1 avoids the current time.
                if int(color_diff[i]) > int(user_inputs[i]):
                    warning = True
                    warning_counter = 0
                    current_time = datetime.datetime.now()
                    data = (current_time, color_diff[0], color_diff[1], color_diff[2],
                            len(colors) + 1, len(colors_per_second) + 1, i,
                            test_color[0], test_color[1], test_color[2])
                    color_change_data.append(data)
                    if webhook_url:
                        card = pymsteams.connectorcard(webhook_url)
                        message = (
                            f"""Color change at {current_time} and {time.time() - rxn_start_time} seconds into reaction. 
                                Red delta: {color_diff[0]}. 
                                Green delta: {color_diff[1]}. 
                                Blue delta: {color_diff[2]}. 
                                """)
                        card.text(message)
                        assert card.send()
                        break

        # If a color change is detected, a warning message is displayed.
        if warning:
            # start is top left, end is bottom right
            # want text to be above start[1] and in the middle of end[0] - start[0]
            text = 'COLOR CHANGE DETECTED'
            (text_width, text_height), _ = cv2.getTextSize(text, font, 1, 3)
            x = (width - text_width) // 2
            # y = height // 8 + text_height // 2
            height_diff = start[1] - 200 + text_height
            y = height_diff if height_diff > 0 else height + height_diff
            frame = cv2.putText(frame, text, (x, y), font, 1,
                                (255, 0, 0), 3)

        # start and end are determined from the original ROI changer.
        frame = cv2.rectangle(frame, start, end, rectangle_color, thickness)

        # This finds the average of all the pixel values in the square for one frame
        reds = []
        greens = []
        blues = []

        for r in range(start[1] + thickness, end[1] - thickness):
            for c in range(start[0] + thickness, end[0] - thickness):
                pixel = frame[r][c]  # List of the 3 RGB values as [B, G, R]
                blues.append(pixel[0])
                greens.append(pixel[1])
                reds.append(pixel[2])

        average_red = np.mean(reds)
        average_green = np.mean(greens)
        average_blue = np.mean(blues)

        current_time = datetime.datetime.now()
        frame_average_color = [average_red, average_green, average_blue, current_time]
        colors.append(frame_average_color)

        frame_counter += 1
        if warning_counter < warning_sign_length:
            warning_counter += 1

        if time_diff >= 1:
            colors_per_second.append(frame_average_color)

        image = av.VideoFrame.from_ndarray(frame, format='bgr24')
        packet = stream.encode(image)
        output.mux(packet)  # Write the encoded frame to MP4 file.

        x_data.append(len(x_data))
        red_plot.append(frame_average_color[0])
        green_plot.append(frame_average_color[1])
        blue_plot.append(frame_average_color[2])

        ax[0].plot(x_data, red_plot, color='r', label='Red')
        ax[1].plot(x_data, green_plot, color='g', label='Green')
        ax[2].plot(x_data, blue_plot, color='b', label='Blue')

        canvas.draw()

        cv2.imshow("Live webcam video", frame)

        # Press the video window and then 'q' to quit and move on.
        # MAKE SURE NUMLOCK IS TURNED ON (number pad is locked)
        key = cv2.waitKey(1)
        # if key == ord('u'):
        #     current_time = datetime.datetime.now()
        #     notes.append([len(colors) + 1, len(colors_per_second), current_time])
        if key & 0xFF == ord('q'):
            break

    vid.release()
    packet = stream.encode(None)
    output.mux(packet)
    output.close()
    cv2.destroyAllWindows()

    color_df = pd.DataFrame(colors, columns=['Red', 'Green', 'Blue', 'Current time: Date / HH:MM:SS'])
    colors_per_second_df = pd.DataFrame(colors_per_second, columns=['Red', 'Green', 'Blue',
                                                                    'Current time: Date / HH:MM:SS'])
    color_change_df = pd.DataFrame(color_change_data, columns=['Current time: Date / HH:MM:SS',
                                                               'Red Difference',
                                                               'Green Difference',
                                                               'Blue Difference',
                                                               'Color Table Row Number',
                                                               'Colors per Second Table Row Number',
                                                               'Color Detected (red=0, green=1, blue=2)',
                                                               'Red Value',
                                                               'Blue Value',
                                                               'Green Value'])
    # notes_df = pd.DataFrame(notes, columns=['Color Table Row Number of note',
    #                                         'Colors per Second Table Row  Number of note',
    #                                         'Current time: Date / HH:MM:SS'])

def next_page1():
    global camera_index, warning_sign_length, color_detection_time, webhook_url
    camera_index = int(camera_index_entry.get())
    warning_sign_length = int(warning_sign_length_entry.get())
    color_detection_time = int(detection_time_entry.get())
    if not webhook_entry.get():
        webhook_url = ("https://azcollaboration.webhook.office.com/webhookb2/b54ccbde-8107-419e-9cb7-60692f9c3e79@af8e89a3-"
               "d9ac-422f-ad06-cc4eb4214314/IncomingWebhook/d3f21f8d0a94461fa20ec6a31e2aa956/1f1eb231-d47e-41ab-8454-"
               "f4fdf14f73b5/V24CYESB-U5yYFccXnpfXGZZ7cmqd0OewLRWOQOFvOlnw1")
    else:
        webhook_url = webhook_entry.get()

    notebook.tab(0, state="disabled")

    webcam_thread = threading.Thread(target=define_roi, args=(camera_index,))
    webcam_thread.start()

def next_page2():
    global red_value, green_value, blue_value
    red_value = int(red_value_entry.get())
    green_value = int(green_value_entry.get())
    blue_value = int(blue_value_entry.get())

    notebook.tab(1, state="disabled")

    live_thread = threading.Thread(target=live_monitoring, args=(camera_index,))
    live_thread.start()

def save_files():
    color_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                              title="Save Color Data")
    if color_file:
        color_df.to_csv(color_file, mode='w', index=False)

    colors_per_second_file = filedialog.asksaveasfilename(defaultextension=".csv",
                                                          filetypes=[("CSV files", "*.csv")],
                                                          title="Save Colors Per Second Data")
    if colors_per_second_file:
        colors_per_second_df.to_csv(colors_per_second_file, mode='w', index=False)

    color_change_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                                     title="Save Color Change Data")
    if color_change_file:
        color_change_df.to_csv(color_change_file, mode='w', index=False)

    output_video = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")],
                                                     title="Save Video Output")
    if output_video:
        with open(output_video, "wb") as f:
            global output_memory_file
            f.write(output_memory_file.getbuffer())

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Webcam Process")

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True)

    page1 = ttk.Frame(notebook)
    notebook.add(page1, text="ROI Selection")

    page2 = ttk.Frame(notebook)
    notebook.add(page2, text="Live Monitoring")

    page3 = ttk.Frame(notebook)
    notebook.add(page3, text="File Saving")

    tk.Label(page1, text="Camera Index:").grid(row=0, column=0, padx=10, pady=10)
    camera_index_entry = tk.Entry(page1)
    camera_index_entry.grid(row=0, column=1)

    tk.Label(page1, text="Time Elapsed per Color Check (seconds):").grid(row=1, column=0, padx=10, pady=10)
    detection_time_entry = tk.Entry(page1)
    detection_time_entry.grid(row=1, column=1)

    tk.Label(page1, text="Warning Sign Length (frames):").grid(row=2, column=0, padx=10, pady=10)
    warning_sign_length_entry = tk.Entry(page1)
    warning_sign_length_entry.grid(row=2, column=1)

    tk.Label(page1, text="Webhook Url (don't enter anything for default):").grid(row=3, column=0, padx=10, pady=10)
    webhook_entry = tk.Entry(page1)
    webhook_entry.grid(row=3, column=1)

    tk.Button(page1, text="Select Region of Interest", command=next_page1).grid(row=4, columnspan=2, pady=10)

    tk.Label(page2, text="Red Value Change:").grid(row=0, column=0, padx=10, pady=10)
    red_value_entry = tk.Entry(page2)
    red_value_entry.grid(row=0, column=1)

    tk.Label(page2, text="Green Value Change:").grid(row=1, column=0, padx=10, pady=10)
    green_value_entry = tk.Entry(page2)
    green_value_entry.grid(row=1, column=1)

    tk.Label(page2, text="Blue Value Change:").grid(row=2, column=0, padx=10, pady=10)
    blue_value_entry = tk.Entry(page2)
    blue_value_entry.grid(row=2, column=1)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    tk.Button(page2, text="Start Live Monitoring", command=next_page2).grid(row=3, columnspan=2, pady=10)

    tk.Label(page3, text="File Saving:").grid(row=0, column=0, padx=10, pady=10)

    tk.Button(page3, text="Save Files", command=save_files).grid(row=1, columnspan=2, pady=10)

    root.mainloop()