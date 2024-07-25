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
from src import eventActionTriggerConstants as EATC

event_callback_created = ()
dictionary_sent = {}

class mock_logger:
    def __init__(self, name=None):
        self.name = name

    def info(self, message):
        print("mock info called with message: " + message)

    def setLevel(self, level):
        pass

    def addHandler(self, hdlr):
        pass

    def removeHandler(self, hdlr):
        pass

@pytest.fixture
def mock_all_relevant_functions(monkeypatch: pytest.MonkeyPatch):
    '''
    This fixture mocks all the relevant functions needed.

    mock_logger_info mocks the logging, and does nothing, as we do not want the
    tests to actually log anything

    mock_event_trigger_cb mocks the event_trigger_cb function, so we can capture
    and use assertions to check that the correct event is created

    mock_update_logs_and_server mocks the update_logs_and_server function, so
    we can see what data is being sent, and we can assert to test
    '''
    def mock_event_trigger_cb(event):
        global event_callback_created
        event_callback_created = event

    def mock_update_logs_and_server(dictionary):
        global dictionary_sent
        dictionary_sent = dictionary
    
    monkeypatch.setattr("eventActionTriggers.event_trigger_cb", 
                        mock_event_trigger_cb)
    monkeypatch.setattr(eventsMod, "update_logs_and_server", mock_update_logs_and_server)
    monkeypatch.setattr("eventsMod.update_logs_and_server",
                        mock_update_logs_and_server)

def test_record_auth_scans(mock_all_relevant_functions):
    '''
    This function tests that record_auth_scans creates the correct event and
    pushes the correct dictionary to the server and its own logs.

    TODO: Assertions are not done yet, create the test cases
    '''
    global event_callback_created, dictionary_sent

    # Remembering original serial number for reset at end of test
    original_logger = eventsMod.logger
    original_serial = eventsMod.controllerSerial

    # Setting test serial
    eventsMod.logger = mock_logger("random_name")
    eventsMod.controllerSerial = "test_serial_123"

    # ------------- TEST SECTION: Record Auth Scan -----------------------------
    eventsMod.record_auth_scans(name=12345, accessGroup="1", authtype="Card", 
                                entrance=1, status="IN")
    
    print("\nEventCB: " + str(event_callback_created))
    print("\nDictionary: " + str(dictionary_sent))
    assert event_callback_created == (EATC.AUTHENTICATED_SCAN, 1)
    assert dictionary_sent["person"] == {"personId": 12345}
    assert dictionary_sent["accessGroup"] == {"accessGroupId": "1"}
    assert dictionary_sent["direction"] == "IN"
    assert dictionary_sent["entrance"] == {"entranceId": 1}
    assert dictionary_sent["eventActionType"] == {"eventActionTypeId": 1} # based on Java side
    assert dictionary_sent["controller"] == {"controllerSerialNo": eventsMod.controllerSerial}

    # ------------- END OF TEST SECTION ----------------------------------------

    event_callback_created = ()
    dictionary_sent = {}

    # Resetting serial number
    eventsMod.logger = original_logger
    eventsMod.controllerSerial = original_serial
