# Project Title: xxxxxxx

## 📝 Description
This project is measures color changes in a user-defined region of interest (ROI) with an easy-to-use graphical user interface (GUI).

---

## 📂 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Instructions](#instructions)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features
- **User-Friendly GUI**: Built with Python and Tkinter
- **Downloadable Executable**: Easy and ready to use.

---

## 🛠️ Installation

### 1. Install the executable
- [GitHub Release](https://github.com/IsaacTieu/color/releases/tag/v1.0)

# OR

### 1. Clone the Repository 
    git clone https://github.com/IsaacTieu/color.git

### 2. Create a Virtual Environment
Create a virtual environment using your preferred tool (e.g., `venv`, `conda`). Here are conda installation instructions.

    cd color
    conda env create -f environment.yml
    conda activate colorenv

---
## 🚀 Usage
The scripts can either be run with the executable, in an IDE or through the command line.

### Run the Executable
1. Double click main.exe
2. This takes ~30 seconds - 1 min to load.

### Run Through an IDE
1. Open `main.py` in your preferred IDE.

### Run Through Command Line

    python main.py

---

## 📥 Instructions

### First Screen

- `Camera Index`: Specifies the camera to be accessed.  
  Example: `1` for the first camera. For an external webcam, it is typically `1`.

- `Time Elapsed per Color Check (seconds)`: Specifies the rate in seconds at which pictures are saved.  
  Example: `3` for a picture saved every 3 seconds.

- `Warning Sign Length (frames)`: Duration of a warning sign being displayed on screen in frames.  
  Example: `30` for a message to be displayed for 30 frames. For a 30 frames per second webcam, this would result in the warning sign lasting for 1 second.

- `Webhook URL`: Specifies the webhook to send Microsoft Teams notifications to.  
  Example: `false` for no Microsoft Teams message to be sent.

- `Select Region of Interest (ROI)`: Press this button to select a ROI. This can be done by holding down left click on the mouse and dragging across the screen.

### Second Screen

- `(R/G/B) Value Change`: This represents the R/G/B value change to be detected for each value. These values range from 0-255, so smaller values will detect smaller changes.  
  Example: `256' for no R/G/B value change to be detected.

- `Start Live Monitoring`: Press this button to start the live monitoring.

### Third Screen

- `Save Files`: Press this button to initiate file saving. `.csv` files will be exported containing R/G/B values and time data. A video of the session will be exported as a `.mp4` file.
---

## 🤝 Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📅 Last Updated
This README was last updated on **April 07, 2025**.


