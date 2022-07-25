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
# check flush_output function in eventActionTriggers.py
GEN_OUT_1=1
GEN_OUT_2=2
GEN_OUT_3=3
DOOR_OPEN=4
BUZZER=5
LED=6
NOTIFICATION=7

# entrance numbers
BOTH_ENTRANCE = False
def is_both_entrance(trigger):
    '''helper function to return if trigger is constant BOTH_ENTRANCE'''
    return trigger is BOTH_ENTRANCE

def input_is_timed(event_action_trigger):
    '''return if input is timed (ie contact open)
    
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action id
        
    Returns:
        is_timed (bool): if the event_action_trigger is timed
    '''

    return type(event_action_trigger) == tuple and len(event_action_trigger) == 3

def create_event(event_action_trigger,entrance):
    '''Creates an event ADT (event_action_trigger,entrance)
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action_trigger
        entrance (int): entrance id

    Returns:
        event ADT (a tuple (event_action_trigger,entrance) )
    '''
    return (event_action_trigger,entrance)

def create_timer_event(event_action_trigger,timer_action,entrance):
    '''To create timer events (they require 2 states, start and stop timer)
    
    Args:
        event_action_trigger (check eventActionTriggerConstants.py): event_action id
        timer_action: eventActionTriggerConstants.START_TIMER or eventActionTriggerConstants.STOP_TIMER
        entrance (int): entrance id
        
    Returns:
        timer event ADT (a tuple (event_action_trigger,timer_action) )
    '''
    return (event_action_trigger,timer_action,entrance)

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

def get_event_entrance(event):
    '''Returns the entrance id
    
    Args:
        event: either an event ADT or timer event ADT
        
    Returns:
        entrance (int): entrance id
    '''
    return event[-1]

def get_event_trigger_from_event(event):
    '''returns the event trigger
    
    Args:
        event: either an event adt or timer event adt
        
    Returns:
        event (check eventActionTriggerConstants.py)
    '''
    return event[0]
