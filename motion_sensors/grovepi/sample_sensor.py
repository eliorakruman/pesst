# sensor imports
import grovepi
import time

pir_sensor = 18

grovepi.pinMode(pir_sensor, “INPUT”)

while True:
    try:
        # sensorValue = grovepi.digitalRead(pir_sensor):
        # if(sensorValue == HIGH):
        if grovepi.digitalRead(pir_sensor):
            print('Motion Detected')
        else:
            print('-')
        time.sleep(.2)
    except IOError:
        print('Error')
        
# we can do this without grovepi! using the same as our original motion detection input. so try that if the installation is no good