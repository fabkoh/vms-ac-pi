import RPi.GPIO as GPIO
from time import sleep

# *** Config ***

relayPin0      = 13
magContactPin = 0
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

def unlockRelay():
    print('  EM unlocked')
    toggleRelay(relayPin = relayPin0, activateLevel = 'High', \
                activateMilliSeconds = 3000, deActivateMilliSeconds = 1000, \
                toggleCount = 1)
    #print('  End   test0().')
    return 

# *** Init/Cleanup/Test/Main ***

def init():
    setGpioMode()
    setupRelayPin(relayPin0)
    GPIO.setup(magContactPin, GPIO.IN, GPIO.PUD_UP)
    return

def cleanup():
    cleanupGpio()
    return

def trigger_relay():
    #print('Begin test(), ...')
    init() #setup pins
    unlockRelay()
    #print('End   test().')
    cleanup()
    return

def main():
    init() #setup pins
    #test()
    return

# *** Main ***

if __name__ == '__main__':
    main()
    

# *** End ***