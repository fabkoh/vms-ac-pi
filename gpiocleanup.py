import RPi.GPIO as GPIO
import time

pin=21
while True:
    GPIO.setmode(GPIO.BCM)
    #GPIO.setup(13, GPIO.OUT)
    GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)
    #GPIO.output(19, GPIO.HIGH)
    print(GPIO.input(pin))
    GPIO.cleanup()
    time.sleep(1)