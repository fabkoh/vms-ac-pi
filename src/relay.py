import time

import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import json
import os
from lock import config_lock
from executor import setup_logger, thread_pool_executor

import pigpio
import time
import GPIOconfig
import eventActionTriggerConstants

pi = pigpio.pi()

path = os.path.dirname(os.path.abspath(__file__))


logger = setup_logger('Relay.log')


# everytime relay triggers, mag_status_open = True
# if mag_contact opened but mag_status_open = False, TRIGGER ALARM

config = None
GPIOpins = None

Relay_1 = None
Relay_2 = None

E1_opened = False
E2_opened = False
E1_perm_opened = False
E2_perm_opened = False
E1_previous = None
E2_previous = None

GEN_1_OPEN, GEN_2_OPEN, GEN_3_OPEN = False, False, False


def update_config():
    global config, GPIOpins, Relay_1, Relay_2, GEN_OUT_1, GEN_OUT_2, GEN_OUT_3
    with config_lock:
        f = open(path+'/json/config.json')
        config = json.load(f)
        f.close()

    GPIOpins = config["GPIOpins"]
    Relay_1 = int(GPIOpins["Relay_1"])
    Relay_2 = int(GPIOpins["Relay_2"])
    GEN_OUT_1 = int(GPIOpins["Gen_Out_1"])
    GEN_OUT_2 = int(GPIOpins["Gen_Out_2"])
    GEN_OUT_3 = int(GPIOpins["Gen_Out_3"])


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
    '''
    This function sets the relay pin to high, meaning it will be activated
    in real life.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
    '''
    GPIO.output(relayPin, GPIO.HIGH)
    return


def setRelayPinLow(relayPin):
    '''
    This function sets the relay pin to low, meaning it will be deactivated
    in real life.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
    '''
    GPIO.output(relayPin, GPIO.LOW)
    return

# *** Relay set/toggle ***
def setRelay(relayPin, activateLevel):
    '''
    This function either activates or deactivates the relay pin based on the
    activateLevel parameter. If the activateLevel is 'High', the relay pin is
    set to high, otherwise it is set to low.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
        activateLevel (str): The level to set the relay pin to. Can be 'High' 
            or 'Low'
    '''
    if activateLevel == 'High':
        setRelayPinHigh(relayPin)
    else:
        setRelayPinLow(relayPin)
    return


# NOTE: toggleRelay1 and toggleRelay2 are essentially doing the exact same thing
#and can be combined into a single function. The only difference is that the
#logging is different.
def toggleRelay1(relayPin, activateMilliSeconds, deActivateMilliSeconds):
    '''
    This function toggles the relay pin on and off based on the 
    activateMilliSeconds for the number of toggleCount times.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
        activateMilliSeconds (int): The number of milliseconds to activate the
            relay pin
        deActivateMilliSeconds (int): The number of milliseconds to deactivate
            the relay pin
    '''
    global E1_opened

    if not E1_opened:
        setGpioMode()
        setupRelayPin(relayPin)

        setRelay(relayPin, 'High')
        E1_opened = True
        sleep(activateMilliSeconds / 1000)

        if E1_perm_opened:
            pass
        else:
            E1_opened = False
            setRelay(relayPin, 'Low')
            sleep(deActivateMilliSeconds / 1000)

    return


def toggleRelay2(relayPin, activateMilliSeconds, deActivateMilliSeconds):
    '''
    This function toggles the relay pin on and off based on the
    activateMilliSeconds for the number of toggleCount times.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
        activateMilliSeconds (int): The number of milliseconds to activate the
            relay pin
        deActivateMilliSeconds (int): The number of milliseconds to deactivate
            the relay pin
        toggleCount (int): The number of times to toggle
    '''
    global E2_opened

    if not E2_opened:
        setGpioMode()
        setupRelayPin(relayPin)
        
        setRelay(relayPin, 'High')
        E2_opened = True
        sleep(activateMilliSeconds / 1000)
            
        if E2_perm_opened:
            pass
        else:
            E2_opened = False
            setRelay(relayPin, "Low")
            sleep(deActivateMilliSeconds / 1000)

    return


# Events Management: Output actions timer for GENOUT_1/2/3
def toggleRelayGen(relayPin, activateMilliSeconds, GenNo):
    '''
    This function toggles the relay pin on and off based on the
    activateMilliSeconds, only once.

    Parameters:
        relayPin (int): The GPIO pin number of the relay
        activateMilliSeconds (int): The number of milliseconds to activate the
            relay pin
        GenNo (int): The number for the general pin being toggled
    '''
    global GEN_1_OPEN, GEN_2_OPEN, GEN_3_OPEN, E1_opened, E2_opened
    
    setGpioMode()
    setupRelayPin(relayPin)

    setRelay(relayPin, 'High')
    if (GenNo == 1):
        GEN_1_OPEN = True
    elif (GenNo == 2):
        GEN_2_OPEN = True
    elif (GenNo == 3):
        GEN_3_OPEN = True
    sleep(activateMilliSeconds)
    setRelay(relayPin, 'Low')
    if (GenNo == 1):
        GEN_1_OPEN = False
    elif (GenNo == 2):
        GEN_2_OPEN = False
    elif (GenNo == 3):
        GEN_3_OPEN = False
    while (GEN_1_OPEN or GEN_2_OPEN or GEN_3_OPEN or E1_opened or E2_opened):
        sleep(1)
    return


def trigger_relay_one(thirdPartyOption=None):
    '''
    This function triggers relay 1, to unlock or do other actions depending on
    whether the thirdPartyOption is set. If the thirdPartyOption is set, the
    outputPin is set to the corresponding GPIO pin number, else it will be
    default Relay_1.

    Parameters:
        thirdPartyOption (str): The third party option to set the outputPin to
        (optional)
    '''
    outputPin = Relay_1

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3

    try:
        thread_pool_executor.submit(toggleRelay1, outputPin, 'High', 5000, 1000, 1)
    except RuntimeError:
        print("Entrance is still opened")
    return


def trigger_relay_two(thirdPartyOption=None):
    '''
    This function triggers relay 2, to unlock or do other actions depending on
    whether the thirdPartyOption is set. If the thirdPartyOption is set, the
    outputPin is set to the corresponding GPIO pin number, else it will be
    default Relay_2.

    Parameters:
        thirdPartyOption (str): The third party option to set the outputPin to
        (optional)
    '''
    outputPin = Relay_2

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3

    try:
        thread_pool_executor.submit(toggleRelay2, outputPin, 'High', 5000, 1000, 1)
    except RuntimeError:
        print("Entrance is still opened")
    return

def lock_unlock_entrance_one(thirdPartyOption=None, unlock=False):
    '''
    This function locks or unlocks entrance one based on the unlock parameter.
    There is also a thirdPartyOption parameter that can be set to use a TPO
    instead of the door. 

    Parameters:
        thirdPartyOption (str): The third party option to set the outputPin to
        (optional)
        unlock (bool): Whether to unlock or lock the entrance
    '''
    outputPin = Relay_1

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3

    global E1_perm_opened
    global E1_previous

    if (E1_previous != None and E1_previous != outputPin):
        setRelay(E1_previous, 'Low')
        E1_previous = None

    if unlock:
        try:
            E1_perm_opened = True
            E1_previous = outputPin
            setGpioMode()
            setupRelayPin(outputPin)
            setRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still opened")
    else:
        try:
            E1_perm_opened = False
            E1_previous = None
            if (not E1_opened):
                setGpioMode()
                setupRelayPin(outputPin)
                setRelay(outputPin, 'Low')
        except RuntimeError:
            print("Entrance is still closed")
    return

def lock_unlock_entrance_two(thirdPartyOption=None, unlock=False):
    '''
    This function locks or unlocks entrance two based on the unlock parameter.
    There is also a thirdPartyOption parameter that can be set to use a TPO
    instead of the door.

    Parameters:
        thirdPartyOption (str): The third party option to set the outputPin to
        (optional)
        unlock (bool): Whether to unlock or lock the entrance
    '''
    outputPin = Relay_2

    if thirdPartyOption == "GEN_OUT_1":
        outputPin = GEN_OUT_1
    if thirdPartyOption == "GEN_OUT_2":
        outputPin = GEN_OUT_2
    if thirdPartyOption == "GEN_OUT_3":
        outputPin = GEN_OUT_3

    global E2_perm_opened
    global E2_previous

    if (E2_previous != None and E2_previous != outputPin):
        setRelay(E2_previous, 'Low')
        E2_previous = None

    if unlock:
        try:
            E2_perm_opened = True
            E2_previous = outputPin
            setGpioMode()
            setupRelayPin(outputPin)
            setRelay(outputPin, 'High')
        except RuntimeError:
            print("Entrance is still opened")
    else:
        try:
            E2_perm_opened = False
            E2_previous = None
            if (not E2_opened):
                setGpioMode()
                setupRelayPin(outputPin)
                setRelay(outputPin, 'Low')
        except RuntimeError:
            print("Entrance is still closed")
    return


def open_GEN_OUT(GEN_OUT_NAME=None, timer=1000, GenNo=1):
    '''
    This function only serves to open a specific GEN_OUT pin, for a specific
    amount of time based on timer.

    Parameters:
        GEN_OUT_PIN (str): The GEN_OUT pin to open
        timer (int): The amount of time to keep the GEN_OUT pin open
        GenNo (int): The number for the general pin being toggled
    '''
    outputPin = None

    if GEN_OUT_NAME == "GEN_OUT_1":
        outputPin = GEN_OUT_1
    if GEN_OUT_NAME == "GEN_OUT_2":
        outputPin = GEN_OUT_2
    if GEN_OUT_NAME == "GEN_OUT_3":
        outputPin = GEN_OUT_3
    
    try:
        thread_pool_executor.submit(toggleRelayGen, outputPin, 'High', timer, GenNo)
    except RuntimeError:
        print(f" {GEN_OUT_NAME} still opened")
    return


def main():
    trigger_relay_one()
    trigger_relay_two()


if __name__ == '__main__':
    main()
