import pigpio
import json
from threading import Lock
import os

# Assuming `path` is defined somewhere to point to your JSON configuration file.
path = os.path.dirname(os.path.abspath(__file__))
config_lock = Lock()

config = None
GPIOpins = None

Fire = None
Relay_1 = None
Relay_2 = None

E1_IN_D0 = None
E1_IN_D1 = None
E1_IN_Buzz = None
E1_IN_Led = None
E1_OUT_D0 = None
E1_OUT_D1 = None
E1_OUT_Buzz = None
E1_OUT_Led = None
E1_Mag = None
E1_Button = None

E2_IN_D0 = None
E2_IN_D1 = None
E2_IN_Buzz = None
E2_IN_Led = None
E2_OUT_D0 = None
E2_OUT_D1 = None
E2_OUT_Buzz = None
E2_OUT_Led = None
E2_Mag = None
E2_Button = None

Gen_In_1 = None
Gen_Out_1 = None
Gen_In_2 = None
Gen_Out_2 = None
Gen_In_3 = None
Gen_Out_3 = None

# initializing pi
pi = pigpio.pi()

def update_config():
    '''call program.update_config() after calling this'''
    global config, GPIOpins, Fire, Relay_1, Relay_2, E1_IN_D0, E1_IN_D1, E1_IN_Buzz, \
        E1_IN_Led, E1_OUT_D0, E1_OUT_D1, E1_OUT_Buzz, E1_OUT_Led, E1_Mag, E1_Button, \
        E2_IN_D0, E2_IN_D1, E2_IN_Buzz, E2_IN_Led, E2_OUT_D0, E2_OUT_D1, E2_OUT_Buzz, \
        E2_OUT_Led, E2_Mag, E2_Button, Gen_In_1, Gen_Out_1, Gen_In_2, Gen_Out_2, \
        Gen_In_3, Gen_Out_3

    f=open(path+'/json/config.json')
    config=json.load(f)
    f.close()

    GPIOpins = config["GPIOpins"]

    Fire = int(GPIOpins["Fire"])
    Relay_1 = int(GPIOpins["Relay_1"])
    Relay_2 = int(GPIOpins["Relay_2"])

    E1_IN_D0 = int(GPIOpins["E1_IN_D0"])
    E1_IN_D1 = int(GPIOpins["E1_IN_D1"])
    E1_IN_Buzz = int(GPIOpins["E1_IN_Buzz"])
    E1_IN_Led = int(GPIOpins["E1_IN_Led"])
    E1_OUT_D0 = int(GPIOpins["E1_OUT_D0"])
    E1_OUT_D1 = int(GPIOpins["E1_OUT_D1"])
    E1_OUT_Buzz = int(GPIOpins["E1_OUT_Buzz"])
    E1_OUT_Led = int(GPIOpins["E1_OUT_Led"])
    E1_Mag = int(GPIOpins["E1_Mag"])
    E1_Button = int(GPIOpins["E1_Button"])

    E2_IN_D0 = int(GPIOpins["E2_IN_D0"])
    E2_IN_D1 = int(GPIOpins["E2_IN_D1"])
    E2_IN_Buzz = int(GPIOpins["E2_IN_Buzz"])
    E2_IN_Led = int(GPIOpins["E2_IN_Led"])
    E2_OUT_D0 = int(GPIOpins["E2_OUT_D0"])
    E2_OUT_D1 = int(GPIOpins["E2_OUT_D1"])
    E2_OUT_Buzz = int(GPIOpins["E2_OUT_Buzz"])
    E2_OUT_Led = int(GPIOpins["E2_OUT_Led"])
    E2_Mag = int(GPIOpins["E2_Mag"])
    E2_Button = int(GPIOpins["E2_Button"])

    try:
        Gen_In_1= int(GPIOpins["Gen_In_1"])
        pi.set_mode(Gen_In_1, pigpio.INPUT)    
    except:
        pass

    try:
        Gen_Out_1= int(GPIOpins["Gen_Out_1"])
        pi.set_mode(Gen_Out_1, pigpio.OUTPUT) 
    except:
        pass

    try:
        Gen_In_2= int(GPIOpins["Gen_In_2"])
        pi.set_mode(Gen_In_2, pigpio.INPUT)    
    except:
        pass

    try:
        Gen_Out_2= int(GPIOpins["Gen_Out_2"])
        pi.set_mode(Gen_Out_2, pigpio.OUTPUT) 
    except:pass

    try:
        Gen_In_3= int(GPIOpins["Gen_In_3"])
        pi.set_mode(Gen_In_3, pigpio.INPUT)    
    except:pass

    try:
        Gen_Out_3= int(GPIOpins["Gen_Out_3"])
        pi.set_mode(Gen_Out_1, pigpio.OUTPUT) 

    except:
        pass
    # initializing inputs
    input_pins = [Fire, E1_IN_D0, E1_IN_D1, E1_OUT_D0, E1_OUT_D1, E2_IN_D0, E2_IN_D1, E2_OUT_D0, E2_OUT_D1, 
                  Gen_In_1, Gen_In_2, Gen_In_3, E1_Mag, E1_Button, E2_Mag, E2_Button]
    
    for pin in input_pins:
        pi.set_mode(pin, pigpio.INPUT)
    
    # initializing outputs
    output_pins = [Relay_1, Relay_2, Gen_Out_1, Gen_Out_2, Gen_Out_3, E1_IN_Buzz, E1_IN_Led, 
                   E1_OUT_Buzz, E1_OUT_Led, E2_IN_Buzz, E2_IN_Led, E2_OUT_Buzz, E2_OUT_Led]
    
    for pin in output_pins:
        pi.set_mode(pin, pigpio.OUTPUT)

def callback_function(gpio, level, tick):
    print(f"Pin {gpio} detected a change to level {level} at tick {tick}")

update_config()  # initialize

# Set up callbacks for input pins
input_pins = [Fire, E1_IN_D0, E1_IN_D1, E1_OUT_D0, E1_OUT_D1, E2_IN_D0, E2_IN_D1, E2_OUT_D0, E2_OUT_D1, 
              Gen_In_1, Gen_In_2, Gen_In_3, E1_Mag, E1_Button, E2_Mag, E2_Button]

# for pin in input_pins:
#     pi.callback(pin, pigpio.EITHER_EDGE, callback_function)
 
# Keep the program running to monitor the pins
try:
    while True:
        pi.write(18,1)
except KeyboardInterrupt:
    pi.stop()
