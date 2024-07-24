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
def mock_logging(monkeypatch: pytest.MonkeyPatch):
    '''
    This is a fixture to mock the logging, and the mock function does nothing,
    as we do not want the tests to create actual logs
    '''
    def mock_logger_info(string, *args, **kwargs):
        pass

    monkeypatch.setattr("logger.info", mock_logger_info)

@pytest.fixture
def mock_event_callbacks(monkeypatch: pytest.MonkeyPatch):
    '''
    This is a fixture to mock the event_trigger_cb function, to capture the
    event being created, so we can assert and check that it was correct
    '''
    def mock_event_trigger_cb(event):
        global event_callback_created
        event_callback_created = event

    monkeypatch.setattr("eventActionTriggers.event_trigger_cb", 
                        mock_event_trigger_cb)

@pytest.fixture
def mock_updating_etlas_logs(monkeypatch: pytest.MonkeyPatch):
    '''
    This is a fixture to mock the update_logs_and_server function, so that we
    can capture what was sent, and check if it was correct using assertions
    '''
    def mock_update_logs_and_server(dictionary):
        global dictionary_sent
        dictionary_sent = dictionary
    
    monkeypatch.setattr("eventsMod.update_logs_and_server", 
                        mock_update_logs_and_server)
