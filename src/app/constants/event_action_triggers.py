"""
This file contains the eventActionInputId and eventActionOutputId of eventActions
DO NOT MODIFY THESE VALUES UNLESS THE JAVA SIDE IS MODIFIED AS WELL
"""

from enum import Enum, auto

# Input Events
class InputEvent(Enum):
    AUTHENTICATED_SCAN = 1  # check eventsMod.py record_auth_scans
    UNAUTHENTICATED_SCAN = 2  # check eventsMod.py record_unauth_scans
    EXIT_BUTTON_PRESSED = 3  # check eventsMod.py record_button_pressed
    CONTACT_OPEN_WITHOUT_AUTHENTICATION = 4  # check eventsMod.py record_mag_opened_warning
    CONTACT_OPEN_WITH_AUTHENTICATION = 5  # check eventsMod.py record_mag_opened
    FIRE = 6  # fire pin, check program.py check_gen_and_fire_pins
    GEN_IN_1 = 7  # check program.py check_gen_and_fire_pins
    GEN_IN_2 = 8  # check program.py check_gen_and_fire_pins
    GEN_IN_3 = 9  # check program.py check_gen_and_fire_pins
    CONTACT_OPEN = 10  # check eventMod.py record_mag_opened, record_mag_opened_warning, record_mag_closed

# Timer Actions
class TimerAction(Enum):
    START_TIMER = auto()
    STOP_TIMER = auto()

# Output Events
class OutputEvent(Enum):
    GEN_OUT_1 = 1
    GEN_OUT_2 = 2
    GEN_OUT_3 = 3
    DOOR_OPEN = 4
    BUZZER = 5
    LED = 6
    SMS_NOTIFICATION = 7
    EMAIL_NOTIFICATION = 8

# Entrance Constants
BOTH_ENTRANCES = False

def is_both_entrances(trigger):
    """Helper function to return if trigger is constant BOTH_ENTRANCES."""
    return trigger is BOTH_ENTRANCES

def input_is_timed(event_action_trigger):
    """Return if input is timed (i.e., contact open).

    Args:
        event_action_trigger (Enum): Input event action trigger.

    Returns:
        bool: True if the event_action_trigger is timed, otherwise False.
    """
    return isinstance(event_action_trigger, tuple) and len(event_action_trigger) == 3

def create_event(event_action_trigger, entrance):
    """Create an event ADT.

    Args:
        event_action_trigger (Enum): Input event action trigger.
        entrance (int): Entrance ID.

    Returns:
        tuple: Event ADT (event_action_trigger, entrance).
    """
    return (event_action_trigger, entrance)

def create_timer_event(event_action_trigger, timer_action, entrance):
    """Create a timer event.

    Args:
        event_action_trigger (Enum): Input event action trigger.
        timer_action (TimerAction): Timer action (START_TIMER or STOP_TIMER).
        entrance (int): Entrance ID.

    Returns:
        tuple: Timer event ADT (event_action_trigger, timer_action, entrance).
    """
    return (event_action_trigger, timer_action, entrance)

def get_timer_event_event_action_trigger(timer_event):
    """Return the event action trigger from the timer event.

    Args:
        timer_event (tuple): Timer event ADT.

    Returns:
        Enum: Event action trigger.
    """
    return timer_event[0]

def get_timer_event_timer_action(timer_event):
    """Return the timer action from the timer event.

    Args:
        timer_event (tuple): Timer event ADT.

    Returns:
        TimerAction: Timer action.
    """
    return timer_event[1]

def get_event_entrance(event):
    """Return the entrance ID from the event.

    Args:
        event (tuple): Event ADT.

    Returns:
        int: Entrance ID.
    """
    return event[-1]

def get_event_trigger_from_event(event):
    """Return the event trigger from the event.

    Args:
        event (tuple): Event ADT.

    Returns:
        Enum: Event trigger.
    """
    return event[0]
