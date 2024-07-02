import os
import sys
import json

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
