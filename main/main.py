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
import threading
import queue
isrunning = {'running': True}


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

print("\nWelcome.")
print("\nWhat did one snowman say to the other snowman? Smells like carrots.")

# CSV Writer - Save for remote usage
'''
print(f"Opening output data file @ {OUTPUT_DATA_PATH")
writer = csv.writer(open(OUTPUT_DATA_PATH, "w+"))
writer.writerow(HEADERS)
print(f"Output data file is open @ {OUTPUT_DATA_PATH}.")
'''
# Create Devices
print("Creating Devices...")
'''
i2c = board.I2C()
pwmdriver = PCA9685(i2c)
pwmdriver.frequency = 60
'''
gamepad = Controller()
print("Devices are good to go.")

# Arduino's map function
def map(x, inmin, inmax, outmin, outmax):
    return (x - inmin) * (outmax - outmin) / (inmax - inmin) + outmin

print("Beginning threading...")
# Set up threading for simultaneous controller reading and robot function
def getinputs(q):
    print("Successfully began input thread.")
    while True:
        if isrunning['running'] == False:
            break

        # Process inputs from gamepad
        inputkeys = gamepad.readinputs()
        q.put(inputkeys)

def processinputs(q):
    print("Successfully began process thread.")
    while True:
        
        if isrunning['running'] == False:
            break

        inputkeys = q.get()
        print("Seeing inputs: " + str(inputkeys))
        # Ends threading loop if select button is pressed
        if inputkeys["BTN_SELECT"] == 1:
            print("Exiting activity loop.")
            isrunning['running'] = False
       
        abs_y = inputkeys["ABS_Y"]
        
        #Account for dead zones on joystick movement
        if abs_y > 0 and abs_y < 2500:
            abs_y = 2500
        elif abs_y > -2500 and abs_y < 0:
            abs_y = -2500
        elif abs_y < -25000:
            abs_y = -25000
        elif abs_y > 25000:
            abs_y = 25000

        # For some reason, negative is up on the gamepad. This flips that. 
        abs_y *= -1

        # Scales joystick input to pwm output (12-bit)
        if abs_y > 0:
            drivepwmout = map(abs_y, 2500, 25000, 2048, 4095)
        else: 
            drivepwmout = map(abs_y, -25000, -2500, 0, 2047)
        dpoleft = drivepwmout
        dporight = drivepwmout
        '''
        pwmdriver.channels[0].duty_cycle = dpoleft
        pwmdriver.channels[1].duty_cycle = dporight
        '''
# Activate threading
q = queue.Queue()

inpthread = threading.Thread(target=getinputs, args=(q,))
processthread = threading.Thread(target=processinputs, args=(q,))

inpthread.start()
processthread.start()
print("Threading is good to go.")

# Main Activity Loop
print("Entering activity loop...")

while isrunning['running'] == True:

    print('here2')
    time.sleep(1)
    print('here3')

 

print("All exited gracefully. Goodbye!")
