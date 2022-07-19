import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import multitasking
import json
import os
path = os.path.dirname(os.path.abspath(__file__))


#everytime relay triggers, mag_status_open = True 
# if mag_contact opened but mag_status_open = False, TRIGGER ALARM 

config = None
GPIOpins = None

Relay_1 = None
Relay_2 = None

def update_config():
    global config, GPIOpins, Relay_1, Relay_2
    f=open(path+'/json/config.json')
    config=json.load(f)
    f.close()

    GPIOpins=config["GPIOpins"]
    Relay_1=int(GPIOpins["Relay_1"])
    Relay_2=int(GPIOpins["Relay_2"])

update_config()
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


# # insert a parameter to determine whether to use GEN_OUT_1/2/3 
# # third_party_option -> null, GEN_OUT_1/2/3
# def trigger_relay_one(third_party_options):

#     if third_party_options:
#         setGpioMode()
#         setupRelayPin(third_party_options)
    
#         try:
#             toggleRelay(relayPin = third_party_options, activateLevel = 'High', \
#                     activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
#                     toggleCount = 1)
#             cleanupGpio()
#         except RuntimeError:
#             print("Entrance is still opened 'third-party-options'.")

#         return


#     setGpioMode()
#     setupRelayPin(Relay_1)
    
#     print(" EM 1 unlocked at " + str(datetime.now()))
#     try:
#         toggleRelay(relayPin = Relay_1, activateLevel = 'High', \
#                 activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
#                 toggleCount = 1)
#         cleanupGpio()
#     except RuntimeError:
#         print("Entrance is still opened")

#     return


@multitasking.task
def trigger_relay_one(thirdPartyOption = None):
    if thirdPartyOption != "N.A.":
        print("THIRD PARTY OPTION")

    else:
        setGpioMode()
        setupRelayPin(Relay_1)
        
        print(" EM 1 unlocked at " + str(datetime.now()))
        try:
            toggleRelay(relayPin = Relay_1, activateLevel = 'High', \
                    activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
                    toggleCount = 1)
            cleanupGpio()
        except RuntimeError:
            print("Entrance is still opened")
        print("test")
    return

@multitasking.task
def trigger_relay_two(thirdPartyOption = None):
    if thirdPartyOption != "N.A.":
        print("THIRD PARTY OPTION")

    else:
        setGpioMode()
        setupRelayPin(Relay_2)
        
        print('  EM 2 unlocked')
        try:
            toggleRelay(relayPin = Relay_2, activateLevel = 'High', \
                    activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
                    toggleCount = 1)
            cleanupGpio()
        except RuntimeError:
            print("Entrance is still opened")
    return

@multitasking.task
def unlock_entrance_one():

    setGpioMode()
    setupRelayPin(Relay_1)
    
    print(" EM 1 unlocked at " + str(datetime.now()))
    try:
        activateRelay(Relay_1, 'High')
    except RuntimeError:
        print("Entrance is still opened")

    return

@multitasking.task
def lock_entrance_one():

    setGpioMode()
    setupRelayPin(Relay_1)
    
    print(" EM 1 locked at " + str(datetime.now()))
    try:
        deActivateRelay(Relay_1, 'High')
    except RuntimeError:
        print("Entrance is still opened")

    return

@multitasking.task
def unlock_entrance_two():

    setGpioMode()
    setupRelayPin(Relay_2)
    
    print(" EM 2 unlocked at " + str(datetime.now()))
    try:
        activateRelay(Relay_2, 'High')
    except RuntimeError:
        print("Entrance is still opened")

    return

@multitasking.task
def lock_entrance_two():

    setGpioMode()
    setupRelayPin(Relay_2)
    
    print(" EM 2 locked at " + str(datetime.now()))
    try:
        deActivateRelay(Relay_2, 'High')
    except RuntimeError:
        print("Entrance is still opened")

    return

def main():
    trigger_relay_one()
    trigger_relay_two()

if __name__ == '__main__':
    main()
