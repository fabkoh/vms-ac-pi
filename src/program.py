import asyncio
import GPIOconfig
import events
import threading
import pigpio
import eventsMod
import healthcheck
import eventsMod
import gc
import piProperty
from executor import thread_pool_executor

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
    print("mag_and_button starting")
    cb1 = GPIOconfig.pi.callback(
        events.E1_Mag, pigpio.RISING_EDGE, events.mag_detects_rising)
    cb2 = GPIOconfig.pi.callback(
        events.E1_Mag, pigpio.FALLING_EDGE, events.mag_detects_falling)
    cb3 = GPIOconfig.pi.callback(
        events.E2_Mag, pigpio.RISING_EDGE, events.mag_detects_rising)
    cb4 = GPIOconfig.pi.callback(
        events.E2_Mag, pigpio.FALLING_EDGE, events.mag_detects_falling)
    cb5 = GPIOconfig.pi.callback(
        events.E1_Button, pigpio.FALLING_EDGE, events.button_detects_change)
    cb6 = GPIOconfig.pi.callback(
        events.E2_Button, pigpio.FALLING_EDGE, events.button_detects_change)


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

    # if timeout_mag.status():
    #     if timeout_mag.check(MAG_TIMEOUT):
    #         GPIOconfig.activate_buzz_led(entrance[:2])

    #         if not timeout_buzzer.status():
    #             timeout_buzzer.start()
    #             print("Buzzer started buzzing")
    #             eventsMod.record_buzzer_start(entrancename)
    #             events.updateserver.update_server_events()

                
    # else:
    #     GPIOconfig.deactivate_buzz_led(entrance[:2])
    #     if timeout_buzzer.status():
    #         timeout_buzzer.stop()
    #         print("Buzzer stopped buzzing")
    #         eventsMod.record_buzzer_end(entrancename)

    events.time.sleep(0.1)


# E1_is_active/E2_is_active
def check_entrance_E1():
    if not events.E1_is_active:
        events.relay.unlock_entrance_one()
    else:
        events.relay.lock_entrance_one()
        if events.verify_datetime(events.E1_entrance_schedule):
            events.relay.unlock_entrance_one()
        else:
            events.relay.lock_entrance_one()

# E1_is_active/E2_is_active


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
    print("check_events_timer starting")
    while True:
        check_events_for("E1_IN")
        check_events_for("E1_OUT")
        check_events_for("E2_IN")
        check_events_for("E2_OUT")
        events.check_entrance_status()
        gc.collect()

        # check_entrance_E1()
        # check_entrance_E2()

def check_gen_pins_and_alarm():
    print("check_gen_pins_and_alarm starting")
    import eventActionTriggers
    import eventActionTriggerConstants

    def helper(pin, event_trigger):
        '''
        Args:
            pin: gpio_pin
            event_trigger: input_event_trigger from eventTriggerConstants
        '''
        def f(gpio, level, tick):
            print("helper called")
            if gpio == pin:
                eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_event(
                    event_trigger, eventActionTriggerConstants.BOTH_ENTRANCE))

        return f

    if GPIOconfig.Gen_In_1 != None:
        cb1 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_1, pigpio.RISING_EDGE, helper(
            GPIOconfig.Gen_In_1, eventActionTriggerConstants.GEN_IN_1))
    if GPIOconfig.Gen_In_2 != None:
        cb2 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_2, pigpio.RISING_EDGE, helper(
            GPIOconfig.Gen_In_2, eventActionTriggerConstants.GEN_IN_2))
    if GPIOconfig.Gen_In_3 != None:
        cb3 = GPIOconfig.pi.callback(GPIOconfig.Gen_In_3, pigpio.RISING_EDGE, helper(
            GPIOconfig.Gen_In_3, eventActionTriggerConstants.GEN_IN_3))
    cb4 = GPIOconfig.pi.callback(GPIOconfig.Fire, pigpio.RISING_EDGE, eventsMod.fire_alarm_activated)

# WARNING READ DESCRIPTION


def update_config():
    '''call this after calling GPIOconfig.update_config(), events.update_config() and events.update_credOccur()
WARNING THIS FUNCTION DOES NOT WORK
it adds an addtion detect_bits call, so multiple detect_bits are called after card scan'''
    global E1_IN, E1_OUT, E2_IN, E2_OUT
    ''' check if decoders are enabled, cancel if true '''
    if E1_IN:
        E1_IN.cancel()
    if E1_OUT:
        E1_OUT.cancel()
    if E2_IN:
        E2_IN.cancel()
    if E2_OUT:
        E2_OUT.cancel()

    E1_IN = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E1_IN_D0,
                               GPIOconfig.E1_IN_D1, events.reader_detects_bits, "E1_IN")
    E1_OUT = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E1_OUT_D0,
                                GPIOconfig.E1_OUT_D1, events.reader_detects_bits, "E1_OUT")

    E2_IN = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E2_IN_D0,
                               GPIOconfig.E2_IN_D1, events.reader_detects_bits, "E2_IN")
    E2_OUT = GPIOconfig.decoder(GPIOconfig.pi, GPIOconfig.E2_OUT_D0,
                                GPIOconfig.E2_OUT_D1, events.reader_detects_bits, "E2_OUT")


def memory_checker():
    piProperty.log_system_stats(1*60*10, 1*60*60*24*5)


update_config()


thread_pool_executor.submit(check_events_timer)
thread_pool_executor.submit(mag_and_button)
thread_pool_executor.submit(check_gen_pins_and_alarm)
thread_pool_executor.submit(memory_checker)
