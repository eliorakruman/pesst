import machine
import neopixel
import time
import random
import math

n = 60  # Number of LEDs
pin = machine.Pin(1) 
np = neopixel.NeoPixel(pin, n)

def set_red_colors():
    np[i] = (255, 0, 0)
    np.write()
    
def set_green_colors():
    np[i] = (0, 255, 0)
    np.write()
    
def set_blue_colors():
    np[i] = (0, 0, 255)
    np.write()
    
def set_white_colors():
    np[i] = (255, 255, 255)
    np.write()

def flash_lights(r, g, b):
    for i in range(n):
        np[i] = (r, g, b) 
    np.show()
    time.sleep(.02)

def demo(np):
    n = np.n
    
    # clear
    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()

while True:
    # Flash all LEDs with random colors
    #set_random_colors()  # Set random colors
    #time.sleep(0.1)  # Short pause to create a dynamic effect

    # Flash lights to simulate beats
    #flash_lights(255, 0, 0)  # Flash Red
    #flash_lights(0, 255, 0)  # Flash Green
    #flash_lights(0, 0, 255)  # Flash Blue

    # Create a wave effect with random colors
    #wave_effect(0, 255, 0)  # Yellow wave
    
    demo(np)
    
    #wave_effect(0, 0, 255)  # Cyan wave

    # Set more random colors for a lively, pulsing effect
    #set_random_colors()
    #time.sleep(0.2)

