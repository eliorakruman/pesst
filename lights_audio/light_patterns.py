import machine
import neopixel
import time
import random
import math

n = 60  # Number of LEDs
pin = machine.Pin(1) 
np = neopixel.NeoPixel(pin, n)

def set_random_colors():
    for i in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        np[i] = (r, g, b)
    np.write() 

def flash_lights(r, g, b):
    for i in range(n):
        np[i] = (r, g, b) 
    np.show()
    time.sleep(.02)

def demo(np):
    n = np.n

    # cycle
    for i in range(4 * n):
       for j in range(n):
           np[j] = (0, 0, 0)
       np[i % n] = (255, 255, 255)
       np.write()
       time.sleep_ms(25)

    # bounce
    for i in range(4 * n):
        for j in range(n):
            np[j] = (0, 0, 128)
        if (i // n) % 2 == 0:
            np[i % n] = (0, 0, 0)
        else:
            np[n - 1 - (i % n)] = (0, 0, 0)
        np.write()
        time.sleep_ms(60)

    # fade in/out
    for i in range(0, 4 * 256, 8):
       for j in range(n):
           if (i // 256) % 2 == 0:
               val = i & 0xff
           else:
               val = 255 - (i & 0xff)
           np[j] = (val, 0, 0)
       np.write()

    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()
# wave effect 
def wave_effect(r, g, b):
    
    for i in range(n):
        b += 4
        g -= 4
        np[i] = (r, g, b)
        np.show()
        time.sleep(.0000000000000002)


while True:
    # Flash all LEDs with random colors
    set_random_colors()  # Set random colors
    time.sleep(0.1)  # Short pause to create a dynamic effect

    # Flash lights to simulate beats
    flash_lights(255, 0, 0)  # Flash Red
    flash_lights(0, 255, 0)  # Flash Green
    flash_lights(0, 0, 255)  # Flash Blue

    wave_effect(0, 255, 0)  # Yellow wave
    
    demo(np)
    
    wave_effect(0, 0, 255)  # Cyan wave

    # Ppulsing effect
    set_random_colors()
    time.sleep(0.2)
