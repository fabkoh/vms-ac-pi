import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from GPIOconfig import Relay_1, Relay_2



#everytime relay triggers, mag_status_open = True 
# if mag_contact opened but mag_status_open = False, TRIGGER ALARM 



# *** GPIO Setp/Cleanup ***

def setGpioMode():
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    return

def cleanupGpio(): 
    GPIO.cleanup()
    return

# *** Relay pin setup/set high/low ***

def setupRelayPin(relayPin):
    GPIO.setup(relayPin, GPIO.OUT)
    GPIO.output(relayPin, GPIO.LOW)  
    return

def setRelayPinHigh(relayPin):
    GPIO.output(relayPin, GPIO.HIGH)
    return

def setRelayPinLow(relayPin):
    GPIO.output(relayPin, GPIO.LOW)
    return

# *** Relay activate/deactivate/toggle ***

def activateRelay(relayPin, activateLevel):
    if activateLevel == 'High':
        setRelayPinHigh(relayPin)
    else:
        setRelayPinLow(relayPin)
    return

def deActivateRelay(relayPin, activateLevel):
    if activateLevel == 'High':
        setRelayPinLow(relayPin)
    else:
        setRelayPinHigh(relayPin)
    return

def toggleRelay(relayPin, activateLevel, activateMilliSeconds, deActivateMilliSeconds, toggleCount):
    for i in range(toggleCount):
        activateRelay(relayPin, activateLevel)
        sleep(activateMilliSeconds / 1000)
        deActivateRelay(relayPin, activateLevel)
        sleep(deActivateMilliSeconds / 1000)
    return

# *** Tests ***

# *** Toggle Relay ***

def trigger_relay_one():

    setGpioMode()
    setupRelayPin(Relay_1)
    
    print(" EM 1 unlocked at " + str(datetime.now()))
    toggleRelay(relayPin = Relay_1, activateLevel = 'High', \
                activateMilliSeconds = 3000, deActivateMilliSeconds = 1000, \
                toggleCount = 1)

    cleanupGpio()
    return

def trigger_relay_two():

    setGpioMode()
    setupRelayPin(Relay_2)
    
    print('  EM 2 unlocked')
    toggleRelay(relayPin = Relay_2, activateLevel = 'High', \
                activateMilliSeconds = 3000, deActivateMilliSeconds = 1000, \
                toggleCount = 1)

    cleanupGpio()
    return



def main():
    trigger_relay_one()
    trigger_relay_two()

if __name__ == '__main__':
    main()