import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(4, GPIO.OUT)


while True:
    print('off')
    GPIO.output(4,False)
    time.sleep(2)
    print('on')
    GPIO.output(4,True)
    time.sleep(2)
