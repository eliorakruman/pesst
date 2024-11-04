from machine import Pin
import time

miniPir = Pin(18, Pin.IN)

while True:
    try:
        if miniPir.value()==1:
            print('Motion Detected')
        else:
            print('-')
        time.sleep(.2)
    except IOError:
        print('Error')