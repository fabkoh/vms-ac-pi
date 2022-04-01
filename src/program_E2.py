from GPIOconfig import *
from events import *
import threading
import pigpio 
import eventsMod

'''
    1. main program that runs E2
    2. when detects any events, imports events.py
    3. checks for API calls
'''

E2_IN = decoder(pi, E2_IN_D0, E2_IN_D1, reader_detects_bits,"E2_IN") 
E2_OUT = decoder(pi, E2_OUT_D0, E2_OUT_D1, reader_detects_bits,"E2_OUT")


def mag():
    cb1 = pi.callback(E2_Mag, pigpio.RISING_EDGE, mag_detects_rising)
    cb2 = pi.callback(E2_Mag, pigpio.FALLING_EDGE, mag_detects_falling)
    
def button():
    
    cb3 = pi.callback(E2_Button, pigpio.RISING_EDGE, button_detects_change)
    
def check_events_timer():
    while True:
        if timeout_cred.status(): 
            if timeout_cred.check(CRED_TIMEOUT):
                timeout_cred.stop()
                del credentials [:]
                del pinsvalue[:]
        
        if timeout_buzzer.status():
            if timeout_buzzer.check(BUZZER_TIMEOUT):
                print("email")
            
        if timeout_mag.status():
            if timeout_mag.check(MAG_TIMEOUT):
                activate_buzz_led()
                if not timeout_buzzer.status():
                    timeout_buzzer.start()
                    eventsMod.record_buzzer("MainDoor","Buzzer started buzzing")
                    api.update_server_events()
        else:
            deactivate_buzz_led()
            if timeout_buzzer.status():
                timeout_buzzer.stop()
                eventsMod.record_buzzer("MainDoor","Buzzer stopped buzzing")
                api.update_server_events()

        time.sleep(0.1)
        
t1 = threading.Thread(target=button)
t2 = threading.Thread(target=mag)
t3 = threading.Thread(target=check_events_timer)

t1.start()
t2.start()
t3.start()