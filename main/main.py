import inputs
import cowsay
import board
import logging
import csv
from datetime import datetime
from adafruit_pca9685 import PCA9685
import adafruit_servokit
import time
from controller import Controller
'''
This is the main program file for the robot's functionality. This script is intended to run
on robot startup and runs until disconnected.
'''
# Setup Data Outputs - Save for remote usage
# Will replace all print statements with logging.debug
'''
OUTPUT_DIRECTORY = "/home/screw/main/logs"
HEADERS = [
        "Time",
        "Joystick Left",
        "Joystick Right"
        ]



now = datetime.now().strfttime("%m_%d_%Y_%H_%M_%S")

OUTPUT_DATA_PATH = f"{OUTPUT_DIRECTORY}/testlog_{now}.csv"
OUTPUT_LOG_PATH = f"{OUTPUT_DIRECTORY}/testlog_{now}.log"
logging.basicConfig(filename=OUTPUT_LOG_PATH, level=logging.DEBUG, filemode="w")
logging.getLogger().addHandler(logging.StreamHandler())
'''

# Jokes

print("\nWhat did one snowman say to the other snowman? Smells like carrots.")
print("Welcome.")

# CSV Writer - Save for remote usage
'''
print(f"Opening output data file @ {OUTPUT_DATA_PATH")
writer = csv.writer(open(OUTPUT_DATA_PATH, "w+"))
writer.writerow(HEADERS)
print(f"Output data file is open @ {OUTPUT_DATA_PATH}.")
'''
# Create Devices
print("Creating Devices")
'''
i2c = board.I2C()
pwmdriver = PCA9685(i2c)
'''
gamepad = Controller()
print("Devices are good to go")

print("Entering activity loop")
running = True

# Main activity loop
while running:
    inputkeys = gamepad.readinputs() 
    

    # Ends activity loop if select button is pressed
    if inputkeys["BTN_SELECT"] == 1:
        running = False

        print("Exiting activity loop.")



print("Activity Loop Exited. Goodbye")
