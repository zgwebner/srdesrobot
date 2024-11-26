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
import RPi.GPIO as GPIO
import adafruit_tcs34725

globalvars = {'running': True, 'launchcolor': 'R', 'pwmworking': True, 'sensorworking': True}


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
print("Successfully imported modules. ")

# Jokes
print("\nWhat did one snowman say to the other snowman? Smells like carrots.\n")

# Create Devices
print("Creating Devices...")

# General Device Setup  
i2c = board.I2C()
GPIO.setmode(GPIO.BCM)
motorlpin = 0
motorrpin = 1
gate1pin = 2
gate2pin = 3
gate3pin = 4

# PWM Driver - driving and sorting
try:
    pwmdriver = PCA9685(i2c)
    pwmdriver.frequency = 60
    pwmdriver.channels[motorlpin].duty_cycle = 32768 
    pwmdriver.channels[motorrpin].duty_cycle = 32768    
    pwmdriver.channels[gate1pin].duty_cycle = 0
    pwmdriver.channels[gate2pin].duty_cycle = 0
    pwmdriver.channels[gate3pin].duty_cycle = 0
except:
    globalvars['pwmworking'] = False
    print("ERROR: PWM driver not connected")

# Color Sensor
try:
    sensor = adafruit_tcs34725.TCS34725(i2c)
    sensor.integration_time = 150
    sensor.gain = 60
except:
    globalvars['sensorworking'] = False
    print("ERROR: Color sensor not connected")

# Pins for GPIO Outputs
actuatepin = 4
launchpin = 20
collectpin = 21
GPIO.setup(actuatepin, GPIO.OUT)
GPIO.setup(collectpin, GPIO.OUT)
GPIO.setup(launchpin, GPIO.OUT)
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
        if globalvars['running'] == False:
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
    highspeed = False
    actuator = False
    launchmotor = False
    collectmotor = False
    while True:
        
        # Closes process thread if stop is detected
        if globalvars['running'] == False:
            print("Closing process thread.")
            break
        (code, state) = q.get()

        # Ends threading loop if select button is pressed
        if code == "BTN_SELECT" and state == 1:
            print("Exiting activity loop.")
            globalvars['running'] = False
        
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

        # Actuator Open or Close
        if code == "BTN_SOUTH" and state == 1:
            if actuator: 
                actuator = False
                print("Closing Actuator")
                GPIO.output(actuatepin, False)
            elif not actuator:
                actuator = True
                print("Opening Actuator")
                GPIO.output(actuatepin, True)

        # Launch Motor ON/OFF
        if code == "BTN_EAST" and state == 1:
            if launchmotor: 
                launchmotor = False
                print("Stopping Launch Motor")
                GPIO.output(launchpin, False)
            elif not launchmotor:
                launchmotor = True
                print("Starting Launch Motor")
                GPIO.output(launchpin, True)

        # Collection Motor ON/OFF
        if code == "BTN_WEST" and state == 1:
            if collectmotor: 
                collectmotor = False
                print("Stopping Collection Motor")
                GPIO.output(collectpin, False)
            elif not collectmotor:
                collectmotor = True
                print("Starting Collection Motor")
                GPIO.output(collectpin, True)

        # Select Blue as Launch Color
        if code == "ABS_HAT0X" and state == 1:
            globalvars['launchcolor'] = 'B'
            print("Launch color set to BLUE")
        # Select Yellow as Launch Color
        if code == "ABS_HAT0X" and state == -1:
            globalvars['launchcolor'] = 'Y'
            print("Launch color set to YELLOW")
        # Select Red as Launch Color
        if code == "ABS_HAT0Y" and state == 1:
            globalvars['launchcolor'] = 'R'
            print("Launch color set to RED")
        # Open end gate for launching
        if code == "ABS_HAT0Y" and state == -1:
            print("Launch Gate Opened") 
            pwmdriver.channels[gate3pin].duty_cycle = 65535

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
                rmod = map(abs_x, lowdead, highdead, 1, 0.5)
            else:
                rmod = 1
                lmod = map(abs_x, -highdead, -lowdead, 0.5, 1)
            print(f"Absolute xin: {abs_x}")
            print(f"Rmod: {rmod}")
            print(f"Lmod: {lmod}")
        
        # Actually move the robot
        if (code == "ABS_Y" or code == "ABS_RX") and (globalvars['pwmworking'] == True):
            rpw = int(drivepwm*rmod)
            lpw = int(drivepwm*lmod)

            print(f"Outputting to channel 0: {rpw}") 
            print(f"Outputting to channel 1: {lpw}")
            
            pwmdriver.channels[motorrpin].duty_cycle = rpw
            pwmdriver.channels[motorlpin].duty_cycle = lpw


# Activate threading
q = queue.Queue()

inpthread = threading.Thread(target=getinputs, args=(q,))
processthread = threading.Thread(target=processinputs, args=(q,))

inpthread.start()
processthread.start()
print("Threading is good to go.")

# Main Activity Loop
print("Entering main loop...")
count = 0
thiscol = 'R'
calibrated = False

while globalvars['running'] == True:


    # Color sort
    if globalvars['sensorworking']:
        color = sensor.color
        rgb = sensor.color_rgb_bytes
        count += 1
        if count == 5:
            initcol = rgb 
            calibrated = True
            print("Color Sensor Calibrated.")
        
        if calibrated:
            if rgb[0] > initcol[0] + 5 and rgb[1] > initcol[1] + 5:
                print(f"Detected YELLOW with rgb values {rgb}.")
            elif rgb[0] > initcol[0] + 10:
                print(f"Detected RED with rgb values {rgb}.")
            elif rgb[2] > initcol[2] + 5:
                print(f"Detected BLUE with rgb values {rgb}.")
            else: 
                print(f"Detected NONE with rgb values {rgb}.")
               

            match globalvars['launchcolor']:
                case 'R':
                    pass
                case 'Y':
                    pass
                case 'B':
                    pass

        else:
            print("Calibrating sensor...")
    time.sleep(0.5)

 

print("All exited gracefully. Goodbye!")
