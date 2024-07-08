import os
import sys

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import timer

def test_status():
    '''
    This test tests that status() returns true when the timer is still running
    '''
    _timer = timer.Timer()
    _timer.start()
    assert _timer.status()

def test_not_status():
    '''
    This test tests that status() returns false when the timer has stopped 
    running
    '''
    _timer = timer.Timer()
    _timer.start()
    _timer.stop()
    assert not _timer.status()