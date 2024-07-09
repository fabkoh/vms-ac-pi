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

'''
TODO:
- check_for_wiegand is not being used anywhere in the codebase. Delete?
- reader_detects_bits is very nested and hard to test...
'''

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
    
    def mock_lock_unlock_entrance_one(thirdPartyOption=None, unlock=False):
        nonlocal entrance_1_unlocked
        if unlock:
            entrance_1_unlocked = True
        else:
            entrance_1_unlocked = False
    
    def mock_lock_unlock_entrance_two(thirdPartyOption=None, unlock=False):
        nonlocal entrance_2_unlocked
        if unlock:
            entrance_2_unlocked = True
        else:
            entrance_2_unlocked = False

    # Patching functions with respective mock functions
    monkeypatch.setattr(events, "verify_datetime", mock_verify_datetime)
    monkeypatch.setattr("relay.lock_unlock_entrance_one", mock_lock_unlock_entrance_one)
    monkeypatch.setattr("relay.lock_unlock_entrance_two", mock_lock_unlock_entrance_two)
    
    # Actual testing
    events.check_entrance_status()

    assert entrance_1_unlocked and entrance_2_unlocked

    # Setting schedules back to original
    events.E1_entrance_schedule = original_E1_schedule
    events.E2_entrance_schedule = original_E2_schedule

def test_check_entrance_status_e1_open(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that check_entrance status will unlock only E1 when
    only E1 is within schedule. There are multiple mock functions as we
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
    events.E2_entrance_schedule = "close"

    # Creating mock functions so relays aren't actually opened
    def mock_verify_datetime(test_schedule):
        if test_schedule == "open":
            return True
        return False
    
    def mock_lock_unlock_entrance_one(thirdPartyOption=None, unlock=False):
        nonlocal entrance_1_unlocked
        if unlock:
            entrance_1_unlocked = True
        else:
            entrance_1_unlocked = False
    
    def mock_lock_unlock_entrance_two(thirdPartyOption=None, unlock=False):
        nonlocal entrance_2_unlocked
        if unlock:
            entrance_2_unlocked = True
        else:
            entrance_2_unlocked = False

    # Patching functions with respective mock functions
    monkeypatch.setattr(events, "verify_datetime", mock_verify_datetime)
    monkeypatch.setattr("relay.lock_unlock_entrance_one", mock_lock_unlock_entrance_one)
    monkeypatch.setattr("relay.lock_unlock_entrance_two", mock_lock_unlock_entrance_two)
    
    # Actual testing
    events.check_entrance_status()

    assert entrance_1_unlocked and not entrance_2_unlocked

    # Setting schedules back to original
    events.E1_entrance_schedule = original_E1_schedule
    events.E2_entrance_schedule = original_E2_schedule

def test_check_entrance_status_neither_open(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that check_entrance status will not unlock when both
    are not within schedule. There are multiple mock functions as we
    have to ensure that the RPi doesn't actually activate or deactivate relays
    '''
    # Vars for asserting if test succeeded
    entrance_1_unlocked = False
    entrance_2_unlocked = False

    # Saving original schedule to set back at the end of test
    original_E1_schedule = events.E1_entrance_schedule
    original_E2_schedule = events.E2_entrance_schedule

    # Setting dummy schedules for testing
    events.E1_entrance_schedule = "close"
    events.E2_entrance_schedule = "close"

    # Creating mock functions so relays aren't actually opened
    def mock_verify_datetime(test_schedule):
        if test_schedule == "open":
            return True
        return False
    
    def mock_lock_unlock_entrance_one(thirdPartyOption=None, unlock=False):
        nonlocal entrance_1_unlocked
        if unlock:
            entrance_1_unlocked = True
        else:
            entrance_1_unlocked = False
    
    def mock_lock_unlock_entrance_two(thirdPartyOption=None, unlock=False):
        nonlocal entrance_2_unlocked
        if unlock:
            entrance_2_unlocked = True
        else:
            entrance_2_unlocked = False

    # Patching functions with respective mock functions
    monkeypatch.setattr(events, "verify_datetime", mock_verify_datetime)
    monkeypatch.setattr("relay.lock_unlock_entrance_one", mock_lock_unlock_entrance_one)
    monkeypatch.setattr("relay.lock_unlock_entrance_two", mock_lock_unlock_entrance_two)
    
    # Actual testing
    events.check_entrance_status()

    assert not entrance_1_unlocked and not entrance_2_unlocked

    # Setting schedules back to original
    events.E1_entrance_schedule = original_E1_schedule
    events.E2_entrance_schedule = original_E2_schedule

def test_open_door(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that open_door triggers relay one but not two when it is
    called with "E1" as an argument, and vice versa. It also tests for when
    both "E1" and "E2" are called
    '''
    # Vars for checking if open door succeeded
    relay_one_triggered = False
    relay_two_triggered = False

    # Remembering original values to set back at end of test
    original_mag_E1 = events.mag_E1_allowed_to_open
    original_mag_E2 = events.mag_E2_allowed_to_open

    # Mock functions to prevent IRL relay triggers
    def mock_trigger_relay_one(TPO):
        nonlocal relay_one_triggered
        relay_one_triggered = True
    
    def mock_trigger_relay_two(TPO):
        nonlocal relay_two_triggered
        relay_two_triggered = True

    # Patching of mock functions
    monkeypatch.setattr("relay.trigger_relay_one", mock_trigger_relay_one)
    monkeypatch.setattr("relay.trigger_relay_two", mock_trigger_relay_two)

    # Actual testing for entrance 1
    events.open_door("E1")
    assert relay_one_triggered and not relay_two_triggered

    # Reset relay 1 and 2
    relay_one_triggered = False
    relay_two_triggered = False

    # Actual testing for entrance 2
    events.open_door("E2")
    assert not relay_one_triggered and relay_two_triggered

    # Reset relay 1 and 2
    relay_one_triggered = False
    relay_two_triggered = False

    # Actual testing for both entrances
    events.open_door("E1")
    events.open_door("E2")

    assert relay_one_triggered and relay_two_triggered

    # Settings vars back to original
    events.mag_E1_allowed_to_open = original_mag_E1
    events.mag_E2_allowed_to_open = original_mag_E2

def test_open_door_using_entrance_id(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that open_door_using_entrance_id only opens entrance 1 when
    the ID given only matches entrance 1, and same for the other case of
    entrance 2
    '''
    # Vars to check if functions were called
    open_door_E1_called = False
    open_door_E2_called = False

    # Remembering original config to set back at end of test
    original_config = events.config

    # Mock config contents and setting the events.config to the mock
    mock_json_contents = {
        "EntranceName": {
            "E1": 12463,
            "E2": 61347
        },
    }
    events.config = mock_json_contents

    # Mocking so that door doesn't actually open
    def mock_open_door(prefix):
        nonlocal open_door_E1_called, open_door_E2_called
        if prefix == "E1":
            open_door_E1_called = True
        if prefix == "E2":
            open_door_E2_called = True

    # Patching the mock function
    monkeypatch.setattr(events, "open_door", mock_open_door)

    # Multiple tests that only match IDs with entrance 1
    events.open_door_using_entrance_id(12463)
    events.open_door_using_entrance_id(12345)
    events.open_door_using_entrance_id(0)
    events.open_door_using_entrance_id(1)
    assert open_door_E1_called and not open_door_E2_called

    # Resetting the door_called vars
    open_door_E1_called = False
    open_door_E2_called = False

    # Multiple tests that only match IDs with entrance 2
    events.open_door_using_entrance_id(61347)
    events.open_door_using_entrance_id(12345)
    events.open_door_using_entrance_id(0)
    events.open_door_using_entrance_id(1)
    assert not open_door_E1_called and open_door_E2_called

    # Setting config back to original
    events.config = original_config

def test_check_for_masterpassword():
    '''
    This test tests that check_for_masterpassword correctly returns either
    true or false based on the json credOccur and the inputs
    '''
    # Mocking part of credOccur
    mock_json_contents = [
        {
            "Entrance": 1,
            "EntranceDetails": {
                "AuthenticationDevices": {
                    "IN": {
                        "defaultAuthMethod": "Card",
                        "Masterpassword": 665544,
                        "Direction": "IN",
                        "AuthMethod": []
                    },
                    "OUT": {
                        "defaultAuthMethod": "Card",
                        "Masterpassword": 445566,
                        "Direction": "OUT",
                        "AuthMethod": []
                    }
                }
            }
        }
    ]

    # Remembering original credOccur and then using the mock json
    original_credOccur = events.credOccur
    events.credOccur = mock_json_contents

    # Actual testing
    test_in = events.check_for_masterpassword([665544], 1, "IN")
    test_out = events.check_for_masterpassword([445566], 1, "OUT")
    test_in_fail_cred = not events.check_for_masterpassword([1], 1, "IN")
    test_in_fail_entr = not events.check_for_masterpassword([665544], 2, "IN")
    test_in_fail_dir = not events.check_for_masterpassword([665544], 1, "OUT")

    assert test_in
    assert test_out
    assert test_in_fail_cred
    assert test_in_fail_entr
    assert test_in_fail_dir

    # Setting credOccur back to original
    events.credOccur = original_credOccur
