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