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
    This test tests that get_timer_event_event_action_trigger returns the
    correct event action trigger when called. There are 2 asserts in this test
    '''
    event_action_trigger_1 = EATC.CONTACT_OPEN
    event_action_trigger_2 = EATC.BUZZER

    event_1 = EATC.create_timer_event(event_action_trigger_1, EATC.START_TIMER, 1)
    event_2 = EATC.create_timer_event(event_action_trigger_2, EATC.START_TIMER, 1)

    assert EATC.get_timer_event_event_action_trigger(event_1) == event_action_trigger_1
    assert EATC.get_timer_event_event_action_trigger(event_2) == event_action_trigger_2

def test_get_timer_event_timer_action():
    '''
    This test tests that get_timer_event_timer_action returns the correct event
    action trigger when called. There are 2 asserts in this test
    '''
    timer_action_1 = EATC.START_TIMER
    timer_action_2 = EATC.STOP_TIMER

    event_1 = EATC.create_timer_event(EATC.CONTACT_OPEN, timer_action_1, 1)
    event_2 = EATC.create_timer_event(EATC.CONTACT_OPEN, timer_action_2, 1)

    assert EATC.get_timer_event_timer_action(event_1) == timer_action_1
    assert EATC.get_timer_event_timer_action(event_2) == timer_action_2

def test_get_event_entrance():
    '''
    This test tests that get_event_entrance returns the correct entrance,
    regardless of whether the event is timed or not. There are 4 asserts in
    this test
    '''
    entrances = [1, 2, 3, 4]

    event_1 = EATC.create_event(EATC.AUTHENTICATED_SCAN, entrances[0])
    event_2 = EATC.create_event(EATC.DOOR_OPEN, entrances[1])
    event_3 = EATC.create_timer_event(EATC.CONTACT_OPEN, EATC.START_TIMER, entrances[2])
    event_4 = EATC.create_timer_event(EATC.CONTACT_OPEN, EATC.STOP_TIMER, entrances[3])

    assert EATC.get_event_entrance(event_1) == entrances[0]
    assert EATC.get_event_entrance(event_2) == entrances[1]
    assert EATC.get_event_entrance(event_3) == entrances[2]
    assert EATC.get_event_entrance(event_4) == entrances[3]
