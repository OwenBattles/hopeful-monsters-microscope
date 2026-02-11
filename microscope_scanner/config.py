"""
Configuration parameters for the microscope tiling system.
Adjust these values for your hardware and scanning requirements.
"""

import os

# Serial communication (Arduino)
SERIAL_PORT = "/dev/tty.usbmodem*"  # macOS; use "COM3" on Windows, "/dev/ttyACM0" on Linux
BAUD_RATE = 115200
SERIAL_TIMEOUT = 5.0

# Camera (UVC / Etaluma Luma 620)
CAMERA_INDEX = 0
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

# Grid scanning
GRID_WIDTH = 5   # number of columns
GRID_HEIGHT = 4  # number of rows
STEP_SIZE_X = 1000  # micrometers (or steps, depending on Arduino firmware)
STEP_SIZE_Y = 1000
SETTLE_TIME = 0.5  # seconds to wait after movement before capture

# Output
IMAGE_SAVE_DIRECTORY = os.path.join(os.path.dirname(__file__), "output")
IMAGE_FILENAME_PATTERN = "tile_x{col}_y{row}.png"
