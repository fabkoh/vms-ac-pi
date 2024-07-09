import os
import sys
import datetime
import pytest

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import events
from src import relay

def test_verify_datetime_day():
    '''
    This test tests that verify_datetime correctly returns true when the date is
    today
    '''
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")

    mock_json_contents = {
        today_string_formatted: [
            {
                "endtime": "24:00",
                "starttime": "00:00"
            }
        ]
    }

    assert events.verify_datetime(mock_json_contents)

def test_not_verify_datetime_day():
    '''
    This test tests that verify_datetime correctly returns false when the date 
    is tomorrow
    '''
    tomorrow_datetime = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_string_formatted = tomorrow_datetime.strftime("%Y-%m-%d")

    mock_json_contents = {
        tomorrow_string_formatted: [
            {
                "endtime": "24:00",
                "starttime": "00:00"
            }
        ]
    }

    assert not events.verify_datetime(mock_json_contents)

def test_verify_datetime_time():
    '''
    This test tests that verify_datetime correctly returns true when the data
    is today, and current time is within the timing schedule
    '''
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now()
    curr_hour = now.hour
    hour_before = f"{curr_hour - 1}:00"
    hour_after = f"{curr_hour + 1}:00"

    mock_json_contents = {
        today_string_formatted: [
            {
                "endtime": hour_after,
                "starttime": hour_before
            }
        ]
    }
    
    assert events.verify_datetime(mock_json_contents)

def test_not_verify_datetime_time():
    '''
    This test tests that verify_datetime correctly returns false when the data
    is today, and current time is outside of the timing schedule
    '''
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now()
    curr_hour = now.hour
    hour_before = f"{curr_hour - 1}:00"
    hour_before_2 = f"{curr_hour - 2}:00"

    mock_json_contents = {
        today_string_formatted: [
            {
                "endtime": hour_before,
                "starttime": hour_before_2
            }
        ]
    }
    
    assert not events.verify_datetime(mock_json_contents)

def test_check_entrance_status_both_open(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that check_entrance status will unlock both entrances when
    the entrances are within schedule. There are multiple mock functions as we
    have to ensure that the RPi doesn't actually activate or deactivate relays
    '''
    # Vars for asserting if test succeeded
    entrance_1_unlocked = False
    entrance_2_unlocked = False

    # Saving original schedule to set back at the end of test
    original_E1_schedule = events.E1_entrance_schedule
    original_E2_schedule = events.E2_entrance_schedule

    # Setting dummy schedules for testing
    events.E1_entrance_schedule = "open"
    events.E2_entrance_schedule = "open"

    # Creating mock functions so relays aren't actually opened
    def mock_verify_datetime(test_schedule):
        if test_schedule == "open":
            return True
        return False
    
    def mock_lock_unlock_entrance_one(ThirdPartyOption, unlock):
        nonlocal entrance_1_unlocked
        print("mock lockunlock 1 reached")
        if unlock:
            entrance_1_unlocked = True
        else:
            entrance_1_unlocked = False
    
    def mock_lock_unlock_entrance_two(ThirdPartyOption, unlock):
        nonlocal entrance_2_unlocked
        print("mock lockunlock 1 reached")
        if unlock:
            entrance_2_unlocked = True
        else:
            entrance_2_unlocked = False

    # Patching functions with respective mock functions
    monkeypatch.setattr(events, "verify_datetime", mock_verify_datetime)
    monkeypatch.setattr(relay, "lock_unlock_entrance_one",
                        mock_lock_unlock_entrance_one)
    monkeypatch.setattr(relay, "lock_unlock_entrance_two",
                        mock_lock_unlock_entrance_two)
    
    # Actual testing
    events.check_entrance_status()

    assert entrance_1_unlocked and entrance_2_unlocked

    # Setting schedules back to original
    events.E1_entrance_schedule = original_E1_schedule
    events.E2_entrance_schedule = original_E2_schedule
