import time
import board
from adafruit_pca9685 import PCA9685

i2c = board.I2C()

pca = PCA9685(i2c)
pca.frequency = 50

sc = 3 
smin = 1500
smax = 2150

pca.channels[sc].duty_cycle = int(smax*65535/20000)
print("1")
time.sleep(3)
pca.channels[sc].duty_cycle = int(smin*65535/20000)
time.sleep(3)
pca.channels[sc].duty_cycle = 0

