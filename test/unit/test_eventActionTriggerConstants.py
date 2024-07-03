import os
import sys

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import eventActionTriggerConstants as EATC

def test_is_both_entrance():
    '''
    This test tests that is_both_entrance returns true when the input is
    the defined BOTH_ENTRANCE constant in EATC
    '''
    assert EATC.is_both_entrance(EATC.BOTH_ENTRANCE)

def test_not_is_both_entrance():
    '''
    This test tests that is_both_entrance returns false when the input is not
    the defined BOTH_ENTRANCE constant in EATC
    '''
    assert not EATC.is_both_entrance("randomly blahblah")

def test_input_is_timed():
    '''
    This test tests that input_is_timed returns true when the event given
    is a timed event
    '''
    event = EATC.create_timer_event(EATC.CONTACT_OPEN, EATC.START_TIMER, 1)
    
    assert EATC.input_is_timed(event)

def test_not_input_is_timed():
    '''
    This test tests that input_is_timed returns false when the event given
    is not a timed event
    '''
    event = EATC.create_event(EATC.AUTHENTICATED_SCAN, 1)

    assert not EATC.input_is_timed(event)

def test_create_event():
    '''
    This test tests that create_event creates a 2-tuple with the correct
    values. There are 3 asserts in this test
    '''
    _event_action_trigger = EATC.CONTACT_OPEN_WITH_AUTHENTICATION
    _entrance = 1
    event = EATC.create_event(_event_action_trigger, _entrance)

    assert type(event) is tuple and len(event) == 2
    assert event[0] == _event_action_trigger
    assert event[1] == _entrance

def test_create_timer_event():
    '''
    This test tests that creat_timer_event creates a 3-tuple with the correct
    values. There are 4 asserts in this test
    '''
    _event_action_trigger = EATC.CONTACT_OPEN
    _timer_action = EATC.START_TIMER
    _entrance = 1
    event = EATC.create_timer_event(_event_action_trigger, _timer_action, _entrance)

    assert type(event) is tuple and len(event) == 3
    assert event[0] == _event_action_trigger
    assert event[1] == _timer_action
    assert event[2] == _entrance

def test_get_timer_event_event_action_trigger():
    '''
    This test thats that get_timer_event_event_action_trigger returns the
    correct event action trigger when called. There are 2 asserts in this test
    '''
    event_action_trigger_1 = EATC.CONTACT_OPEN
    event_action_trigger_2 = EATC.BUZZER

    event1 = EATC.create_timer_event(event_action_trigger_1, EATC.START_TIMER, 1)
    event2 = EATC.create_timer_event(event_action_trigger_2, EATC.START_TIMER, 1)

    assert EATC.get_timer_event_event_action_trigger(event1) == event_action_trigger_1
    assert EATC.get_timer_event_event_action_trigger(event2) == event_action_trigger_2