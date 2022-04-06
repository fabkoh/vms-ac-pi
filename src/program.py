from GPIOconfig import *
from events import *
import threading
import pigpio 
import eventsMod

'''
    1. main program that runs everything, including E1
    2. when detects any events, imports events.py
    3. checks for API calls
'''



E1_IN = decoder(pi, E1_IN_D0, E1_IN_D1, reader_detects_bits,"E1_IN") 
E1_OUT = decoder(pi, E1_OUT_D0, E1_OUT_D1, reader_detects_bits,"E1_OUT")


E2_IN = decoder(pi, E2_IN_D0, E2_IN_D1, reader_detects_bits,"E2_IN") 
E2_OUT = decoder(pi, E2_OUT_D0, E2_OUT_D1, reader_detects_bits,"E2_OUT")


def mag_and_button():
    cb1 = pi.callback(E1_Mag, pigpio.RISING_EDGE, mag_detects_rising)
    cb2 = pi.callback(E1_Mag, pigpio.FALLING_EDGE, mag_detects_falling)
    cb3 = pi.callback(E2_Mag, pigpio.RISING_EDGE, mag_detects_rising)
    cb4 = pi.callback(E2_Mag, pigpio.FALLING_EDGE, mag_detects_falling)
    cb5 = pi.callback(E1_Button, pigpio.FALLING_EDGE, button_detects_change)
    cb6 = pi.callback(E2_Button, pigpio.FALLING_EDGE, button_detects_change)

def check_events_for(entrance):
    if entrance.split("_")[0] == "E1":
        entrancename = E1
    if entrance.split("_")[0] == "E2":
        entrancename = E2
    
    if entrance == "E1_IN":
        credentials = credentials_E1_IN
        pinsvalue = pinsvalue_E1_IN
        timeout_cred = timeout_cred_E1_IN
        timeout_mag = timeout_mag_E1
        timeout_buzzer = timeout_buzzer_E1
        CRED_TIMEOUT = CRED_TIMEOUT_E1
        MAG_TIMEOUT = MAG_TIMEOUT_E1
        BUZZER_TIMEOUT = BUZZER_TIMEOUT_E1

    if entrance == "E1_OUT":
        credentials = credentials_E1_OUT
        pinsvalue = pinsvalue_E1_OUT
        timeout_cred = timeout_cred_E1_OUT
        timeout_mag = timeout_mag_E1
        timeout_buzzer = timeout_buzzer_E1
        CRED_TIMEOUT = CRED_TIMEOUT_E1
        MAG_TIMEOUT = MAG_TIMEOUT_E1
        BUZZER_TIMEOUT = BUZZER_TIMEOUT_E1

    if entrance == "E2_IN":
        credentials = credentials_E2_IN
        pinsvalue = pinsvalue_E2_IN
        timeout_cred = timeout_cred_E2_IN
        timeout_mag = timeout_mag_E2
        timeout_buzzer = timeout_buzzer_E2
        CRED_TIMEOUT = CRED_TIMEOUT_E2
        MAG_TIMEOUT = MAG_TIMEOUT_E2
        BUZZER_TIMEOUT = BUZZER_TIMEOUT_E2

    if entrance == "E2_OUT":
        credentials = credentials_E2_OUT
        pinsvalue = pinsvalue_E2_OUT
        timeout_cred = timeout_cred_E2_OUT
        timeout_mag = timeout_mag_E2
        timeout_buzzer = timeout_buzzer_E2
        CRED_TIMEOUT = CRED_TIMEOUT_E2
        MAG_TIMEOUT = MAG_TIMEOUT_E2
        BUZZER_TIMEOUT = BUZZER_TIMEOUT_E2
    
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
                print("Buzzer started buzzing")
                eventsMod.record_buzzer(entrancename,"Buzzer started buzzing")
                updateserver.update_server_events()
    else:
        deactivate_buzz_led()
        if timeout_buzzer.status():
            timeout_buzzer.stop()
            print("Buzzer stopped buzzing")
            eventsMod.record_buzzer(entrancename,"Buzzer stopped buzzing")
            updateserver.update_server_events()

    time.sleep(0.1)


def check_events_timer():
    while True:
        check_events_for("E1_IN")
        check_events_for("E1_OUT")
        check_events_for("E2_IN")
        check_events_for("E2_OUT")
        
t1 = threading.Thread(target=mag_and_button)
t2 = threading.Thread(target=check_events_timer)

t1.start()
t2.start()