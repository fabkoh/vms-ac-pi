import GPIOconfig
import events
import threading
import pigpio 
import eventsMod
import healthcheck

'''
    1. main program that runs everything, including E1
    2. when detects any events, imports events.py
    3. checks for API calls
'''
healthcheck.main(True)

E1_IN = None
E1_OUT = None


E2_IN = None
E2_OUT = None

def mag_and_button():
    cb1 = GPIOconfig.pi.callback(events.E1_Mag, pigpio.RISING_EDGE, events.mag_detects_rising)
    cb2 = GPIOconfig.pi.callback(events.E1_Mag, pigpio.FALLING_EDGE, events.mag_detects_falling)
    cb3 = GPIOconfig.pi.callback(events.E2_Mag, pigpio.RISING_EDGE, events.mag_detects_rising)
    cb4 = GPIOconfig.pi.callback(events.E2_Mag, pigpio.FALLING_EDGE, events.mag_detects_falling)
    cb5 = GPIOconfig.pi.callback(events.E1_Button, pigpio.FALLING_EDGE, events.button_detects_change)
    cb6 = GPIOconfig.pi.callback(events.E2_Button, pigpio.FALLING_EDGE, events.button_detects_change)

def check_events_for(entrance):
    if entrance.split("_")[0] == "E1":
        entrancename = events.E1
    if entrance.split("_")[0] == "E2":
        entrancename = events.E2
    
    if entrance == "E1_IN":
        credentials = events.credentials_E1_IN
        pinsvalue = events.pinsvalue_E1_IN
        timeout_cred = events.timeout_cred_E1_IN
        timeout_mag = events.timeout_mag_E1
        timeout_buzzer = events.timeout_buzzer_E1
        CRED_TIMEOUT = events.CRED_TIMEOUT_E1
        MAG_TIMEOUT = events.MAG_TIMEOUT_E1
        BUZZER_TIMEOUT = events.BUZZER_TIMEOUT_E1

    if entrance == "E1_OUT":
        credentials = events.credentials_E1_OUT
        pinsvalue = events.pinsvalue_E1_OUT
        timeout_cred = events.timeout_cred_E1_OUT
        timeout_mag = events.timeout_mag_E1
        timeout_buzzer = events.timeout_buzzer_E1
        CRED_TIMEOUT = events.CRED_TIMEOUT_E1
        MAG_TIMEOUT = events.MAG_TIMEOUT_E1
        BUZZER_TIMEOUT = events.BUZZER_TIMEOUT_E1

    if entrance == "E2_IN":
        credentials = events.credentials_E2_IN
        pinsvalue = events.pinsvalue_E2_IN
        timeout_cred = events.timeout_cred_E2_IN
        timeout_mag = events.timeout_mag_E2
        timeout_buzzer = events.timeout_buzzer_E2
        CRED_TIMEOUT = events.CRED_TIMEOUT_E2
        MAG_TIMEOUT = events.MAG_TIMEOUT_E2
        BUZZER_TIMEOUT = events.BUZZER_TIMEOUT_E2

    if entrance == "E2_OUT":
        credentials = events.credentials_E2_OUT
        pinsvalue = events.pinsvalue_E2_OUT
        timeout_cred = events.timeout_cred_E2_OUT
        timeout_mag = events.timeout_mag_E2
        timeout_buzzer = events.timeout_buzzer_E2
        CRED_TIMEOUT = events.CRED_TIMEOUT_E2
        MAG_TIMEOUT = events.MAG_TIMEOUT_E2
        BUZZER_TIMEOUT = events.BUZZER_TIMEOUT_E2
    
    if timeout_cred.status(): 
            if timeout_cred.check(CRED_TIMEOUT):
                timeout_cred.stop()
                credentials.clear()
                pinsvalue.clear()
    
    if timeout_buzzer.status():
        if timeout_buzzer.check(BUZZER_TIMEOUT):
            print("email")
        
    if timeout_mag.status():
        if timeout_mag.check(MAG_TIMEOUT):
            GPIOconfig.activate_buzz_led(entrance[:2])
            
            if not timeout_buzzer.status():
                timeout_buzzer.start()
                print("Buzzer started buzzing")
                eventsMod.record_buzzer_start(entrancename)
                events.updateserver.update_server_events()
    else:
        GPIOconfig.deactivate_buzz_led(entrance[:2])
        if timeout_buzzer.status():
            timeout_buzzer.stop()
            print("Buzzer stopped buzzing")
            eventsMod.record_buzzer_end(entrancename)

    events.time.sleep(0.1)


#E1_is_active/E2_is_active
def check_entrance_E1():
    if not events.E1_is_active: 
        events.relay.unlock_entrance_one()
    else:
        events.relay.lock_entrance_one()
        if events.verify_datetime(events.E1_entrance_schedule):
            events.relay.unlock_entrance_one()
        else:
            events.relay.lock_entrance_one()

#E1_is_active/E2_is_active
def check_entrance_E2():
    if not events.E2_is_active: 
        events.relay.unlock_entrance_two()
    else:
        events.relay.lock_entrance_two()
        if events.verify_datetime(events.E2_entrance_schedule):
            events.relay.unlock_entrance_two()
        else:
            events.relay.lock_entrance_two()
    
def check_events_timer():
    while True:
        check_events_for("E1_IN")
        check_events_for("E1_OUT")
        check_events_for("E2_IN")
        check_events_for("E2_OUT")
        #check_entrance_E1()
        #check_entrance_E2()
        
def check_gen_pins_and_alarm():
    import eventActionTriggers
    import eventActionTriggerConstants

    def helper(pin,event_trigger):
        '''
        Args:
            pin: gpio_pin
            event_trigger: input_event_trigger from eventTriggerConstants
        '''
        def f(gpio,level,tick):
            if gpio==pin:
                eventActionTriggers.event_trigger_cb(event_trigger)

        return f

    if GPIOconfig.Gen_In_1 != None:
        cb1 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_1, pigpio.RISING_EDGE, helper(GPIOconfig.Gen_In_1,eventActionTriggerConstants.GEN_IN_1))
    if GPIOconfig.Gen_In_2 != None:
        cb2 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_2,pigpio.RISING_EDGE, helper(GPIOconfig.GEN_IN_2,eventActionTriggerConstants.GEN_IN_2))
    if GPIOconfig.Gen_In_2 != None:
        cb3 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_3,pigpio.RISING_EDGE,helper(GPIOconfig.GEN_IN_3,eventActionTriggerConstants.GEN_IN_3))
    cb4=GPIOconfig.pi.callback(GPIOconfig.Fire,pigpio.RISING_EDGE,helper(GPIOconfig.Fire,eventActionTriggerConstants.FIRE))
    

def update_config():
    '''call this after calling GPIOconfig.update_config(), events.update_config() and events.update_credOccur()'''
    global E1_IN, E1_OUT, E2_IN, E2_OUT
    E1_IN = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E1_IN_D0, GPIOconfig.E1_IN_D1, events.reader_detects_bits,"E1_IN") 
    E1_OUT = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E1_OUT_D0, GPIOconfig.E1_OUT_D1, events.reader_detects_bits,"E1_OUT")

    E2_IN = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E2_IN_D0, GPIOconfig.E2_IN_D1, events.reader_detects_bits,"E2_IN") 
    E2_OUT = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E2_OUT_D0, GPIOconfig.E2_OUT_D1, events.reader_detects_bits,"E2_OUT")

    # including these as need to update the listeners to hear for the new pins
    mag_and_button()
    check_gen_pins_and_alarm()

update_config()

t1 = threading.Thread(target=check_events_timer)
t1.start()