from datetime import datetime
from program import timeout_mag
import relay


def cbmagrise(gpio, level, tick):
    print("Entrance 1 is opened at " + str(datetime.now()))
    timeout_mag.start()

    
def cbmagfall(gpio, level, tick):
    print("Entrance 1 is closed at " + str(datetime.now()))
    mag_status_open = False
    timeout_mag.stop()

def cbbutton(gpio, level, tick):
    print("Pb 1 was pushed at " + str(datetime.now()))
    relay.trigger_relay_one()

