import os
import sys
import json
import datetime
import pytest
import time

TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import eventActionTriggers as EAT
from src import eventActionTriggerConstants as EATC

'''
TODO:
flush_output and check_for_only_timer_based_events are hard 
to test due to many dependencies being used.
'''

# This is so that it can be easily passed into the tests without needing
#to create a new mock json in every test that needs it
@pytest.fixture
def mock_json_eventActionTriggers():
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")
    return [
        {
            "eventsManagementId": 1,
            "eventsManagementName": "authEnter",
            "inputEvents": [
                {
                    "inputEventId": 1,
                    "timerDuration": None,
                    "eventActionInputType": {
                        "eventActionInputId": 1,
                        "eventActionInputName": "AUTHENTICATED SCAN",
                        "timerEnabled": False,
                        "eventActionInputConfig": None
                    }
                }
            ],
            "outputActions": [
                {
                    "outputEventId": 1,
                    "timerDuration": None,
                    "eventActionOutputType": {
                        "eventActionOutputId": 8,
                        "eventActionOutputName": "NOTIFICATION (EMAIL)",
                        "timerEnabled": False,
                        "eventActionOutputConfig": None,
                        "recipents": None,
                        "recipentsMessage": None
                    }
                }
            ],
            "triggerSchedule": {
                today_string_formatted: [
                    {
                        "endtime": "24:00",
                        "starttime": "00:00"
                    }
                ]
            },
            "entrance": {
                "entranceId": 1
            },
            "controller": None
        },
        {
            "eventsManagementId": 2,
            "eventsManagementName": "email",
            "inputEvents": [
                {
                    "inputEventId": 5,
                    "timerDuration": None,
                    "eventActionInputType": {
                        "eventActionInputId": 2,
                        "eventActionInputName": "UNAUTHENTICATED SCAN",
                        "timerEnabled": False,
                        "eventActionInputConfig": None
                    }
                }
            ],
            "outputActions": [
                {
                    "outputEventId": 3,
                    "timerDuration": None,
                    "eventActionOutputType": {
                        "eventActionOutputId": 8,
                        "eventActionOutputName": "NOTIFICATION (EMAIL)",
                        "timerEnabled": None,
                        "eventActionOutputConfig": None,
                        "recipents": None,
                        "recipentsMessage": None
                    }
                }
            ],
            "triggerSchedule": {
                today_string_formatted: [
                    {
                        "endtime": "24:00",
                        "starttime": "00:00"
                    }
                ]
            },
            "entrance": {
                "entranceId": 1
            },
            "controller": None
        }
    ]

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
    says that the current date is within schedule.
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
    says that the current date is not within schedule.
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

def test_get_entrance_from_event_management():
    '''
    This test creates a mock of what will be passed into the get_entrance function,
    with a simulated entrance ID, then verifies that the ID returned by the function
    matches.
    '''
    mock_json_contents = {
        "entrance": {
            "entranceId": 1
        },
    }

    assert EAT.get_entrance_from_event_management(mock_json_contents) == 1

def test_not_get_entrance_from_event_management():
    '''
    This test creates a mock of what will be passed into the get_entrance function,
    with a simulated entrance ID, then verifies that the ID returned by the function
    will not match when it is not supposed to match.
    '''
    mock_json_contents = {
        "entrance": {
            "entranceId": 2
        },
    }

    assert not EAT.get_entrance_from_event_management(mock_json_contents) == 1

def test_get_both_entrance_from_event_management():
    '''
    This test creates a mock of what will be passed into the get_entrance function,
    which in this case is nothing, and verifies that the function is supposed to
    return the same as the BOTH_ENTRANCE constant in EAT
    '''
    mock_json_contents = {}

    assert EAT.get_entrance_from_event_management(mock_json_contents) == EAT.BOTH_ENTRANCE

def test_event_trigger_cb_1(monkeypatch: pytest.MonkeyPatch, mock_json_eventActionTriggers):
    '''
    This test and the one below checks that event_trigger_cb correctly
    queues the correct event to the output_events var upon being called with
    different events (AUTH SCAN and UNAUTH SCAN)
    '''
    # This is to ensure that event_trigger_cb doesn't actually flush the output
    #and trigger things IRL
    def mock_flush_output():
        pass
    monkeypatch.setattr(EAT, "flush_output", mock_flush_output)

    # Remembering of original vars to save back later
    original_output_events = EAT.output_events
    original_JSON_data = EAT.EVENT_ACTION_TRIGGERS_DATA
    original_eventTriggerTime = EAT.eventTriggerTime
    original_activated = EAT.activated

    # Setting EAT vars to defaults
    EAT.output_events = []
    EAT.activated = {}
    EAT.eventTriggerTime = {}
    EAT.EVENT_ACTION_TRIGGERS_DATA = mock_json_eventActionTriggers

    # Testing
    time.sleep(2) # to take into account debounce delay
    event_trigger = EATC.create_event(EATC.AUTHENTICATED_SCAN, 1)
    EAT.event_trigger_cb(event_trigger)
    assert EAT.output_events[0] == mock_json_eventActionTriggers[0]

    # At the end of the test, reset vars
    EAT.output_events = original_output_events
    EAT.EVENT_ACTION_TRIGGERS_DATA = original_JSON_data
    EAT.eventTriggerTime = original_eventTriggerTime
    EAT.activated = original_activated

def test_event_trigger_cb_2(monkeypatch: pytest.MonkeyPatch, mock_json_eventActionTriggers):
    # This is to ensure that event_trigger_cb doesn't actually flush the output
    #and trigger things IRL
    def mock_flush_output():
        pass
    monkeypatch.setattr(EAT, "flush_output", mock_flush_output)

    # Remembering of original vars to save back later
    original_output_events = EAT.output_events
    original_JSON_data = EAT.EVENT_ACTION_TRIGGERS_DATA
    original_eventTriggerTime = EAT.eventTriggerTime
    original_activated = EAT.activated

    # Setting EAT vars to defaults
    EAT.output_events = []
    EAT.activated = {}
    EAT.eventTriggerTime = {}
    EAT.EVENT_ACTION_TRIGGERS_DATA = mock_json_eventActionTriggers

    # Testing
    time.sleep(2) # to take into account debounce delay
    event_trigger = EATC.create_event(EATC.UNAUTHENTICATED_SCAN, 1)
    EAT.event_trigger_cb(event_trigger)
    assert EAT.output_events[0] == mock_json_eventActionTriggers[1]

    # At the end of the test, reset vars
    EAT.output_events = original_output_events
    EAT.EVENT_ACTION_TRIGGERS_DATA = original_JSON_data
    EAT.eventTriggerTime = original_eventTriggerTime
    EAT.activated = original_activated

def test_flush_output(monkeypatch: pytest.MonkeyPatch, mock_json_eventActionTriggers):
    '''
    This test first adds some mock events into EAT.output_events, then calls
    flush_output and checks that the output_events array is empty
    '''
    num_times_called = 0
    def mock_send_email(event):
        global num_times_called
        num_times_called += 1
    monkeypatch.setattr(EAT, "sendEmail_function", mock_send_email)

    EAT.output_events[0] = mock_json_eventActionTriggers[0]
    EAT.output_events[1] = mock_json_eventActionTriggers[1]
    EAT.flush_output()

    assert not EAT.output_events # checks that array is empty
    assert num_times_called == 2