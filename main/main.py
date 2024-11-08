import inputs
import board
import logging
from datetime import datetime
from adafruit_pca9685 import PCA9685
import time
from controller import Controller
import threading
import queue
import numpy
isrunning = {'running': True}


'''
This is the main program file for the robot's functionality. This script is intended to run
on robot startup and runs until disconnected.
'''
# Setup loging output - Save for remote usage
# Will replace all print statements with logging.debug
'''
OUTPUT_DIRECTORY = "/home/screw/main/logs"

now = datetime.now().strfttime("%m_%d_%Y_%H_%M_%S")

OUTPUT_LOG_PATH = f"{OUTPUT_DIRECTORY}/testlog_{now}.log"
logging.basicConfig(filename=OUTPUT_LOG_PATH, level=logging.DEBUG, filemode="w")
logging.getLogger().addHandler(logging.StreamHandler())
'''

print("Welcome.")
print("Successfully imported modules and created log. ")

# Jokes
print("\nWhat did one snowman say to the other snowman? Smells like carrots.\n")

# Create Devices
print("Creating Devices...")

'''
i2c = board.I2C()
pwmdriver = PCA9685(i2c)
pwmdriver.frequency = 60

pwmdriver.channels[0].duty_cycle = 32768 
pwmdriver.channels[1].duty_cycle = 32768
'''         

gamepad = Controller()
print("Devices are good to go.")

# Arduino's map function - extremely useful for pwm signalling
def map(x, inmin, inmax, outmin, outmax):
    return (x - inmin) * (outmax - outmin) / (inmax - inmin) + outmin

print("Beginning threading...")

# Set up threading for simultaneous controller reading and robot function

# Input thread is to constantly read controller input
def getinputs(q):
    print("Successfully began input thread.")
    notsyncinp = False
    while True:
        
        # Closes input thread
        if isrunning['running'] == False:
            print("Closing input thread.")
            break

        # Process inputs from gamepad
        while not notsyncinp:
            code, state, notsyncinp = gamepad.readinputs()
        notsyncinp = False
        q.put((code, state))

# Process thread is to constantly act on read controller input
def processinputs(q):
    print("Successfully began process thread.")
    drivepwm = 32767
    rmod = 1
    lmod = 1
    lowdead = 1000
    highdead = 31000
    pwmin = 16384
    pwmax = 49152
    highspeed = True
    while True:
        
        # Closes process thread if stop is detected
        if isrunning['running'] == False:
            print("Closing process thread.")
            break
        (code, state) = q.get()

        # Ends threading loop if select button is pressed
        if code == "BTN_SELECT" and state == 1:
            print("Exiting activity loop.")
            isrunning['running'] = False
        
        # High speed vs low speed mode
        if code == "BTN_NORTH" and state == 1:
            if highspeed:
                highspeed = False
                pwmin = 16384
                pwmax = 49152
                print("Entering low speed mode")
            elif not highspeed:
                highspeed = True
                pwmin = 0
                pwmax = 65535
                print("Entering high speed mode")

        # Process fwd/back movement
        if code == "ABS_Y":
            abs_y = state
            
            # Account for dead zones on joystick movement
            if abs_y > 0 and abs_y < lowdead:
                abs_y = lowdead
            elif abs_y > -lowdead and abs_y < 0:
                abs_y = -lowdead
            elif abs_y < -highdead:
                abs_y = -highdead
            elif abs_y > highdead:
                abs_y = highdead

            # Scales joystick input to pwm output (12-bit)
            if abs_y > 0:
                drivepwm = map(abs_y, lowdead, highdead, 32767, pwmax)
            else: 
                drivepwm = map(abs_y, -highdead, -lowdead, pwmin, 32767)


        # Calculate Differential Drive
        if code == "ABS_RX":
            abs_x = state

            # Account for dead zones on joystick movement
            if abs_x > 0 and abs_x < lowdead:
                abs_x = lowdead
            elif abs_x > -lowdead and abs_x < 0:
                abs_x = -lowdead
            elif abs_x < -highdead:
                abs_x = -highdead
            elif abs_x > highdead:
                abs_x = highdead

            # Scales relative speed modifier based on steer
            if abs_x > 0:
                lmod = 1
                rmod = map(abs_x, lowdead, highdead, 1, 0.3)
            else:
                rmod = 1
                lmod = map(abs_x, -highdead, -lowdead, 0.3, 1)
            print(f"Absolute xin: {abs_x}")
            print(f"Rmod: {rmod}")
            print(f"Lmod: {lmod}")
        
        # Actually move the robot
        if code == "ABS_Y" or code == "ABS_RX":
            rpw = int(drivepwm*rmod)
            lpw = int(drivepwm*lmod)

            print(f"Outputting to channel 0: {rpw}") 
            print(f"Outputting to channel 1: {lpw}")
            '''
            pwmdriver.channels[0].duty_cycle = rpw
            pwmdriver.channels[1].duty_cycle = lpw
            '''
# Activate threading
q = queue.Queue()

inpthread = threading.Thread(target=getinputs, args=(q,))
processthread = threading.Thread(target=processinputs, args=(q,))

inpthread.start()
processthread.start()
print("Threading is good to go.")

# Main Activity Loop
print("Entering main loop...")

while isrunning['running'] == True:

    print("Main loop running...")
    time.sleep(1)

 

print("All exited gracefully. Goodbye!")
