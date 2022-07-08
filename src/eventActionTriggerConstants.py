'''
This file contains the eventActionInputId and eventActionOutputId of eventActions
DO NOT MODIFY THESE VALUES UNLESS THE JAVA SIDE IS MODIFIED AS WELL
'''

# input
# non timer
AUTHENTICATED_SCAN=1 # check eventsMod.py record_auth_scans
UNAUTHENTICATED_SCAN=2 # check eventsMod.py record_unauth_scans
EXIT_BUTTON_PRESSED=3 # check eventsMod.py record_button_pressed
CONTACT_OPEN_WITHOUT_AUTHENTICATION=4 # check eventsMod.py record_mag_opened_warning
CONTACT_OPEN_WITH_AUTHENTICATION=5 # check eventsMod.py record_mag_opened
FIRE=6 # fire pin, check program.py check_gen_and_fire_pins
GEN_IN_1=7 # check program.py check_gen_and_fire_pins
GEN_IN_2=8 # check program.py check_gen_and_fire_pins
GEN_IN_3=9 # check program.py check_gen_and_fire_pins

# timer (timer ADTs will have 2 fields, id and start/stop timer)
CONTACT_OPEN=10 # check eventMod.py record_mag_opened, record_mag_opened_warning, record_mag_closed

START_TIMER=True
STOP_TIMER=False

# output
GEN_OUT_1=1
GEN_OUT_2=2
GEN_OUT_3=3
EMLOCK_1=4
EMLOCK_2=5

# # id of timer based input events
# TIMED_EVENTS={CONTACT_OPEN} # set for better performance
def input_is_timed(event_action_trigger):
    '''return if input is timed (ie contact open)
    
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action id
        
    Returns:
        is_timed (bool): if the event_action_trigger is timed
    '''

    return type(event_action_trigger) == tuple

def create_timer_event(event_action_trigger,timer_action):
    '''To create timer events (they require 2 states, start and stop timer)
    
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action id
        timer_action: eventActionTriggerConstants.START_TIMER or eventActionTriggerConstants.STOP_TIMER
        
    Returns:
        timer event ADT (a tuple (event_action_trigger,timer_action) )
    '''
    return (event_action_trigger,timer_action)

def get_timer_event_event_action_trigger(timer_event):
    '''Returns timer_event event_action_trigger (timer_event[0])
    
    Args:
        timer_event: timer_event ADT
        
    Returns:
        event_action_trigger: check eventActionTriggerConstants.py
    '''
    return timer_event[0]

def get_timer_event_timer_action(timer_event):
    '''Returns timer_event timer_action (timer_event[1])
    
    Args:
        timer_event: timer_event ADT
        
    Returns:
        timer_action: check eventActionTriggerConstants.py
    '''

    return timer_event[1]