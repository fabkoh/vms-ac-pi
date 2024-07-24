import os
import sys
import pytest

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import eventsMod

event_callback_created = ()
dictionary_sent = {}

@pytest.fixture
def mock_all_relevant_functions(monkeypatch: pytest.MonkeyPatch):
    def mock_logger_info(string, *args, **kwargs):
        pass

    def mock_event_trigger_cb(event):
        global event_callback_created
        event_callback_created = event

    def mock_update_logs_and_server(dictionary):
        global dictionary_sent
        dictionary_sent = dictionary
    
    monkeypatch.setattr("logger.info", mock_logger_info)
    monkeypatch.setattr("eventActionTriggers.event_trigger_cb", 
                        mock_event_trigger_cb)
    monkeypatch.setattr("eventsMod.update_logs_and_server", 
                        mock_update_logs_and_server)
    