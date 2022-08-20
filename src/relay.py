import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import multitasking
import json
import os

from eventActionTriggerConstants import GEN_OUT_1
path = os.path.dirname(os.path.abspath(__file__))


#everytime relay triggers, mag_status_open = True 
# if mag_contact opened but mag_status_open = False, TRIGGER ALARM 

config = None
GPIOpins = None

Relay_1 = None
Relay_2 = None

def update_config():
    global config, GPIOpins, Relay_1, Relay_2, GEN_OUT_1, GEN_OUT_2, GEN_OUT_3
    f=open(path+'/json/config.json')
    config=json.load(f)
    f.close()

    GPIOpins=config["GPIOpins"]
    Relay_1=int(GPIOpins["Relay_1"])
    Relay_2=int(GPIOpins["Relay_2"])
    GEN_OUT_1=int(GPIOpins["Gen_Out_1"])
    GEN_OUT_2=int(GPIOpins["Gen_Out_2"])
    GEN_OUT_3=int(GPIOpins["Gen_Out_3"])

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

    outputPin = Relay_1

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
        print(thirdPartyOption,outputPin)
    
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
        print(thirdPartyOption,outputPin)

    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3
        print(thirdPartyOption,outputPin)

    setGpioMode()
    setupRelayPin(outputPin)
    
    print(" EM 1 unlocked at " + str(datetime.now()))
    try:
        toggleRelay(relayPin = outputPin, activateLevel = 'High', \
                activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
                toggleCount = 1)
        cleanupGpio()
    except RuntimeError:
        print("Entrance is still opened")
    print("test")
    return

@multitasking.task
def trigger_relay_two(thirdPartyOption = None):

    outputPin = Relay_2

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
        print(thirdPartyOption,outputPin)
    
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
        print(thirdPartyOption,outputPin)

    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3
        print(thirdPartyOption,outputPin)


    setGpioMode()
    setupRelayPin(outputPin)
    
    print('  EM 2 unlocked')
    try:
        toggleRelay(relayPin = outputPin, activateLevel = 'High', \
                activateMilliSeconds = 5000, deActivateMilliSeconds = 1000, \
                toggleCount = 1)
        cleanupGpio()
    except RuntimeError:
        print("Entrance is still opened")
    return

@multitasking.task
def lock_unlock_entrance_one(thirdPartyOption = None,unlock=False):

    outputPin = Relay_1

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
        print(thirdPartyOption,outputPin)
    
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
        print(thirdPartyOption,outputPin)

    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3
        print(thirdPartyOption,outputPin)

    setGpioMode()
    setupRelayPin(outputPin)
    
    print(" EM 1 unlocked at " + str(datetime.now()))
    if unlock:
        try:
            activateRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still opened")
    else:
        try:
            deActivateRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still closed")
    print("test")
    return

@multitasking.task
def lock_unlock_entrance_two(thirdPartyOption = None,unlock=False):

    outputPin = Relay_2

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
        print(thirdPartyOption,outputPin)
    
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
        print(thirdPartyOption,outputPin)

    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3
        print(thirdPartyOption,outputPin)

    setGpioMode()
    setupRelayPin(outputPin)
    
    print(" EM 2 unlocked at " + str(datetime.now()))
    if unlock:
        try:
            activateRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still opened")
    else:
        try:
            deActivateRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still closed")
    print("test")
    return

@multitasking.task
def open_GEN_OUT(GEN_OUT_PIN = None, timer = 4000):
        
    outputPin = None

    if GEN_OUT_PIN == "GEN_OUT_1":
        outputPin = GEN_OUT_1
        print(GEN_OUT_PIN,outputPin)
    
    if GEN_OUT_PIN == "GEN_OUT_2":
        outputPin = GEN_OUT_2
        print(GEN_OUT_PIN,outputPin)

    if GEN_OUT_PIN == "GEN_OUT_3":
        outputPin = GEN_OUT_3
        print(GEN_OUT_PIN,outputPin)


    setGpioMode()
    setupRelayPin(outputPin)
    
    print(f" {GEN_OUT_PIN}  unlocked")
    try:
        toggleRelay(relayPin = outputPin, activateLevel = 'High', \
                activateMilliSeconds = timer, deActivateMilliSeconds = 1000, \
                toggleCount = 1)
        cleanupGpio()
    except RuntimeError:
        print(f" {GEN_OUT_PIN} still opened")
    return

# not used
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
