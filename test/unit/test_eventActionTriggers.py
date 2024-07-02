import os
import sys
import json
import datetime

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import eventActionTriggers as EAT
from src import eventActionTriggerConstants as EATC

def test_queue_output():
    '''
    This test ensures that queue_output is actually putting the outputs to 
    the EAT.output_events list.
    '''
    event = EATC.create_event(EATC.AUTHENTICATED_SCAN, 1)
    EAT.queue_output(event)

    assert len(EAT.output_events) == 1

    EAT.output_events = []

def test_update_event_action_triggers():
    ''' 
    This test checks that the update_action_event_triggers function is properly
    loading in the EAT.json file.
    '''
    original_json = open(SRC_DIR + "/src/json/eventActionTriggers.json")
    EAT.update_event_action_triggers()
    assert EAT.EVENT_ACTION_TRIGGERS_DATA == json.load(original_json)

def test_check_datetime():
    '''
    This test creates a mock of what will be passed into the check_datetime function
    and uses 'today', meaning the function should return true since the schedule
    says that the current date is within schedule
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

    assert EAT.check_datetime(mock_json_contents)

def test_not_check_datetime():
    '''
    This test creates a mock of what will be passed into the check_datetime function
    and uses 'tomorrow', meaning the function should return false since the schedule
    says that the current date is not within schedule
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

    assert not EAT.check_datetime(mock_json_contents)