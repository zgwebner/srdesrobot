import time
import board
import adafruit_tcs34725


i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.integration_time = 150
sensor.gain = 60

while True:
    color = sensor.color
    color_rgb = sensor.color_rgb_bytes

    print("RGB color as 8 bits per channel int: #{0:02X} or as 3-tuple: {1}".format(color, color_rgb))

    time.sleep(1)
