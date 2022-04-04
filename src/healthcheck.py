
import pigpio
import json
from datetime import datetime

pi = pigpio.pi()
fileconfig = open('json/config.json')
config = json.load(fileconfig)

GPIOpins = config["GPIOpins"]
readersConnection = config["controllerConfig"]["readersConnection"]

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

def test_for_connection(D0,D1,reader):
    if pi.read(D0) == 1 and pi.read(D1) == 1:
        readersConnection[reader] = "Connected"
    else:
        readersConnection[reader] = ""

test_for_connection(E1_IN_D0,E1_IN_D1,"E1_IN")
test_for_connection(E2_IN_D0,E2_IN_D1,"E1_OUT")
test_for_connection(E1_OUT_D0,E1_OUT_D1,"E2_IN")
test_for_connection(E2_OUT_D0,E2_OUT_D1,"E2_OUT")

now = datetime.now()
current_date_time = now.strftime("%d-%m-%Y %H:%M:%S")
readersConnection["dateAndTime"] = current_date_time