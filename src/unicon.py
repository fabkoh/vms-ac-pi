'''contains the controller code'''
import threading
import time
from json_readers import ConfigContainer, TestJsonContainer
import pigpio
from decoder import Decoder

E1_IN_D0 = None
E1_IN_D1 = None
E1_OUT_D0 = None
E1_OUT_D1 = None

E2_IN_D0 = None
E2_IN_D1 = None
E2_OUT_D0 = None
E2_OUT_D1 = None

E1_IN = None
E1_OUT = None

E2_IN = None
E2_OUT = None

pi = pigpio.pi()

def set_readers_to_read():
    '''Set readers to read, requires config.json ['GPIOpins'] dict'''
    global E1_IN_D0, E1_IN_D1, E1_OUT_D0, E1_OUT_D1, \
           E2_IN_D0, E2_IN_D1, E2_OUT_D0, E2_OUT_D1, \
           E1_IN, E1_OUT, E2_IN, E2_OUT
    
    pins_config = ConfigContainer[0]['GPIOpins']
    E1_IN_D0  = int(pins_config['E1_IN_D0'])
    E1_IN_D1  = int(pins_config['E1_IN_D1'])
    E1_OUT_D0 = int(pins_config['E1_OUT_D0'])
    E1_OUT_D1 = int(pins_config['E1_OUT_D1'])

    E2_IN_D0  = int(pins_config['E2_IN_D0'])
    E2_IN_D1  = int(pins_config['E2_IN_D1'])
    E2_OUT_D0 = int(pins_config['E2_OUT_D0'])
    E2_OUT_D1 = int(pins_config['E2_OUT_D1'])

    pi.set_mode(E1_IN_D0,  pigpio.INPUT)
    pi.set_mode(E1_IN_D1,  pigpio.INPUT)
    pi.set_mode(E1_OUT_D0, pigpio.INPUT)
    pi.set_mode(E1_OUT_D1, pigpio.INPUT)
    
    pi.set_mode(E2_IN_D0,  pigpio.INPUT)
    pi.set_mode(E2_IN_D1,  pigpio.INPUT)
    pi.set_mode(E2_OUT_D0, pigpio.INPUT)
    pi.set_mode(E2_OUT_D1, pigpio.INPUT)

def check_auth_device_status():
    '''checks if auth devices are responding
    Note:
        requires pins to be initialised first
    
    Returns:
        auth_device_status (dict): with keys 'E1IN', 'E1OUT', 'E2IN', 'E2OUT' mapped to bool
    '''
    return {
        'E1IN' : (pi.read(E1_IN_D0) and pi.read(E1_IN_D1)),
        'E1OUT': (pi.read(E1_OUT_D0) and pi.read(E1_OUT_D1)),
        'E2IN' : (pi.read(E2_IN_D0) and pi.read(E2_IN_D1)),
        'E2OUT': (pi.read(E2_OUT_D0) and pi.read(E2_OUT_D1))
    }

def main():
    set_readers_to_read()