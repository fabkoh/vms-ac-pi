
import pigpio
import json

pi = pigpio.pi()
fileconfig = open('json/config.json')
config = json.load(fileconfig)

GPIOpins = config["GPIOpins"]

E1_IN_D0= int(GPIOpins["E1_IN_D0"])
E1_IN_D1= int(GPIOpins["E1_IN_D1"])
pi.set_mode(E1_IN_D0, pigpio.INPUT)
pi.set_mode(E1_IN_D1, pigpio.INPUT)

E1_OUT_D0= int(GPIOpins["E1_OUT_D0"])
E1_OUT_D1= int(GPIOpins["E1_OUT_D1"])
pi.set_mode(E1_OUT_D0, pigpio.INPUT)
pi.set_mode(E1_OUT_D1, pigpio.INPUT)

E2_IN_D0= int(GPIOpins["E2_IN_D0"])
E2_IN_D1= int(GPIOpins["E2_IN_D1"])
pi.set_mode(E2_IN_D0, pigpio.INPUT)
pi.set_mode(E2_IN_D1, pigpio.INPUT)

E2_OUT_D0= int(GPIOpins["E2_OUT_D0"])
E2_OUT_D1= int(GPIOpins["E2_OUT_D1"])
pi.set_mode(E2_OUT_D0, pigpio.INPUT)
pi.set_mode(E2_OUT_D1, pigpio.INPUT)

def test_for_connection(D0,D1):
    if pi.read(D0) == 1 and pi.read(D1) == 1:
        return True
    else:
        return False
    
print(test_for_connection(E1_IN_D0,E1_IN_D1))
print(test_for_connection(E2_IN_D0,E2_IN_D1))
print(test_for_connection(E1_OUT_D0,E1_OUT_D1))
print(test_for_connection(E2_OUT_D0,E2_OUT_D1))