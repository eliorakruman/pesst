# sensor imports
from machine import ADC, Pin
import time
from utime import sleep

# lcd display imports
from lcd1602 import LCD1602
from machine import I2C,Pin

# server imports
import network
import socket

# sensor setup
front_sensor = ADC(Pin(27)) # A1
back_sensor = ADC(Pin(26)) # A0
back_triggered = False
front_triggered = False
hit_max = False

# lcd vars and constants
tally = 0
ticks_since = 0 # to record timing between front and back triggers
diff = 0 # updates tally
COOLDOWN_MULTIPLIER = 15
MAX_CAPACITY = 5

# lcd setup
i2c = I2C(1,scl=Pin(7), sda=Pin(6), freq=400000)
d = LCD1602(i2c, 2, 16)

d.clear()
d.print(str(tally))

# server setup

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('bob')
ip = wlan.ifconfig()[0]
print(f'Connected on {ip}')
while not wlan.isconnected():
    print('Waiting for connection...', wlan.status())
    sleep(3)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("10.42.0.241", 1234))
client.send("motion_sensor".encode())

def convert_to_voltage(adc_value, v_ref=3.3):
    return (adc_value / 65535) * v_ref

def print_lines():
    print(f"Front Light Level (ADC): {f_adc_value}")
    print(f"Front Voltage: {f_voltage:.2f} V")
    print(f"Back Light Level (ADC): {b_adc_value}")
    print(f"Back Voltage: {b_voltage:.2f} V")
    print()

try:
    
    while True:
        ticks_since +=1
    
        # reset ticks if too much time passed
        if ticks_since == COOLDOWN_MULTIPLIER:
            print("cooldown")
            front_triggered = False
            back_triggered = False
            ticks_since = 0
            
        f_adc_value = front_sensor.read_u16()
        f_voltage = convert_to_voltage(f_adc_value)
        
        b_adc_value = back_sensor.read_u16()
        b_voltage = convert_to_voltage(b_adc_value)
        
        if(f_voltage<1.75):
            print_lines()
            ticks_since = 0
            if back_triggered and tally>0: # back then front: someone exited
                diff -=1
                back_triggered = False
                print("exit")
                if hit_max:
                    client.send("white".encode())
                    hit_max = False
            else: # front only: mid-entry
                front_triggered = True
                
        elif(b_voltage<1.75):
            print_lines()
            ticks_since = 0
            if front_triggered: # front then back: someone entered
                diff +=1
                front_triggered = False
                print("enter")
                if tally + diff == MAX_CAPACITY:
                    hit_max = True
                    client.send("blue".encode())
            else: # back only: mid exit
                back_triggered = True
        
        if diff != 0:
            tally += diff
            diff = 0
            if tally <= MAX_CAPACITY:
                d.clear()
                d.print(str(tally))
            else:
                print("")    
        
        time.sleep(.5)

except KeyboardInterrupt:
    print("Program terminated.")
    