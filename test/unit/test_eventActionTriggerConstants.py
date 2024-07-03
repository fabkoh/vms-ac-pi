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

