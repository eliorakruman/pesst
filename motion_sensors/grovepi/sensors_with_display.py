# sensor imports
import grovepi
import time

# lcd display imports
from lcd1602 import LCD1602
from machine import I2C,Pin
from utime import sleep

# sensor setup
front_sensor = 18
grovepi.pinMode(front_sensor, "INPUT")
back_sensor = 20
grovepi.pinMode(back_sensor, "INPUT")

# lcd setup
i2c = I2C(1,scl=Pin(7), sda=Pin(6), freq=400000)
d = LCD1602(i2c, 2, 16)
tally = 0

# variables
back = False

while True:
    try:
        if grovepi.digitalRead(front_sensor) and not back:
            tally +=1
            d.clear()
            d.print(tally)
        elif grovepi.digitalRead(front_sensor):
            back = False
            tally -=1
            d.clear()
            d.print(tally)
        elif grovepi.digitalRead(back_sensor):
            back = True
        else:
            print('-')
        sleep(.2)
    except IOError:
        print('Error')