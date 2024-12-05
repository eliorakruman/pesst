# sensor imports
from machine import ADC, Pin
import time

# lcd display imports
from lcd1602 import LCD1602
from machine import I2C,Pin

#sensor setup
front_sensor = ADC(Pin(26))
back_sensor = ADC(Pin(27))
back_triggered = False
front_triggered = False

# lcd vars and constants
tally = 0
ticks_since = 0 # to record timing between front and back triggers
diff = 0 # updates tally
COOLDOWN_MULTIPLIER = 20
HISTORY_SIZE = 10
MAX_CAPACITY = 5

# lcd setup
i2c = I2C(1,scl=Pin(7), sda=Pin(6), freq=400000)
d = LCD1602(i2c, 2, 16)

d.clear()
d.print(tally)

def convert_to_voltage(adc_value, v_ref=3.3):
    return (adc_value / 65535) * v_ref

try:
    while True:
        ticks_since +=1;
    
        # reset ticks if too much time passed
        if ticks_since == COOLDOWN_MULTIPLIER * HISTORY_SIZE:
            front = False
            back = False
            ticks_since = 0
            
        f_adc_value = front_sensor.read_u16()
        f_voltage = convert_to_voltage(f_adc_value)
        
        b_adc_value = back_sensor.read_u16()
        b_voltage = convert_to_voltage(b_adc_value)
        
        print(f"Front Light Level (ADC): {f_adc_value}")
        print(f"Front Voltage: {f_voltage:.2f} V")
        print(f"Back Light Level (ADC): {b_adc_value}")
        print(f"Back Voltage: {b_voltage:.2f} V")
        
        if(f_voltage<2):
            ticks_since = 0
            if back_triggered: # back then front: someone exited
                diff -=1
                back_triggered = False
                print("exit")
            else: # front only: mid-entry
                front_triggered = True
                
        if(b_voltage<2):
            ticks_since = 0
            if front_triggered: # front then back: someone entered
                diff +=1
                front_triggered = False
                print("enter")
            else: # back only: mid exit
                back_triggered = True
        print()
        
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
    