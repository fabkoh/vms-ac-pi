'''
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
BUZZER = 8
buzzState = False
GPIO.setup(BUZZER,GPIO.OUT)
while True:
    buzzState = not buzzState
    GPIO.output(BUZZER,buzzState)
    time.sleep(1)
'''
import pigpio
import time

def main():
    test = 8
    pi = pigpio.pi()
    pi.set_mode(test, pigpio.OUTPUT)
    while True:     
        pi.write(test, 1)     
        time.sleep(1)    
        pi.write(test, 0)    
        time.sleep(1)
        #pi.write(8, 0)
    
    pi.set_mode(20, pigpio.OUTPUT)
    pi.write(20, 0)
    print(pi.read(20))
    
    time.sleep(2)

    
    #pi.stop


if __name__ == "__main__":
    main()
    