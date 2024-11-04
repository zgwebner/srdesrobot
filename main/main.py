import inputs
import board
import logging
from datetime import datetime
from adafruit_pca9685 import PCA9685
import time
from controller import Controller
import threading
import queue
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

# Jokes
print("Successfully imported modules and created log. ")
print("\nWelcome.")
print("\nWhat did one snowman say to the other snowman? Smells like carrots.\n")

# Create Devices
print("Creating Devices...")

i2c = board.I2C()
pwmdriver = PCA9685(i2c)
pwmdriver.frequency = 60

pwmdriver.channels[0].duty_cycle = 32768 
pwmdriver.channels[1].duty_cycle = 32768
            

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
    while True:

        # Closes input thread
        if isrunning['running'] == False:
            print("Closing input thread.")
            break

        # Process inputs from gamepad
        code, state = gamepad.readinputs()
        
        q.put((code, state))

# Process thread is to constantly act on read controller input
def processinputs(q):
    print("Successfully began process thread.")
    while True:
        
        # Closes process thread
        if isrunning['running'] == False:
            print("Closing process thread.")
            break
        (code, state) = q.get()

        # Ends threading loop if select button is pressed
        if code == "BTN_SELECT" and state == 1:
            print("Exiting activity loop.")
            isrunning['running'] = False

        # Process movement joystick events
        if code == "ABS_Y":
            abs_y = state
            
            # Account for dead zones on joystick movement
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
                drivepwmout = map(abs_y, 2500, 25000, 32768, 65535)
            else: 
                drivepwmout = map(abs_y, -25000, -2500, 0, 32768)

            dpoleft = drivepwmout
            dporight = drivepwmout
            print(f"Outputting to channel 0: {dpoleft}") 
            print(f"Outputting to channel 1: {dporight}")
            
            pwmdriver.channels[0].duty_cycle = int(dpoleft)
            pwmdriver.channels[1].duty_cycle = int(dporight)
            
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
