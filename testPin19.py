import time
import RPi.GPIO as GPIO
from datetime import datetime

GPIO.setmode(GPIO.BCM)
relayPin = 21
GPIO.setup(relayPin, GPIO.IN, GPIO.PUD_UP)
print(GPIO.input(relayPin))
while True: 
    if GPIO.input(relayPin) == 0:
        print(GPIO.input(relayPin))
        print("Pb 2 was pushed at: "+ str(datetime.now()))
        time.sleep(1)
        #relay_two.trigger_relay()
        GPIO.setup(relayPin, GPIO.IN, GPIO.PUD_UP)
        print("After PUD up "+str(GPIO.input(relayPin)))
    
GPIO.cleaup()
print("clean")
