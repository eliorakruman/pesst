# sensor imports
import time

# lcd display imports
from lcd1602 import LCD1602
from machine import I2C,Pin
from utime import sleep

# sensor setup
front_sensor = Pin(16, Pin.IN)
back_sensor = Pin(18, Pin.IN)

# lcd setup
i2c = I2C(1,scl=Pin(7), sda=Pin(6), freq=400000)
d = LCD1602(i2c, 2, 16)
tally = 0
d.clear()

# variables
back = False

while True:
    if front_sensor.value()==1 and not back:
        print("enter")
        tally +=1
        d.clear()
        d.print(str(tally))
        sleep(.5)
    elif front_sensor.value()==1:
        back = False
        print("front")
        tally -=1
        d.clear()
        d.print(str(tally))
        sleep(.5)
    elif back_sensor.value()==1:
        back = True
        print("back")
        sleep(.5)
    else:
        print('-')
    sleep(.2)
        