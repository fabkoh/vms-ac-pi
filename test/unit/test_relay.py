import os
import sys
import pytest
import time

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import relay

relayPinNumber = 0
relayPinSetting = []

@pytest.fixture
def mock_setup_cleanup(monkeypatch: pytest.MonkeyPatch):
    '''
    This is a fixture to mock setGpioMode, setupRelayPin and cleanupGpio, so
    that the GPIO module doesn't actually carry out the setup and cleanup
    operations, as we don't need them.
    '''
    def mock_setGpioMode():
        pass
    
    def mock_setupRelayPin(relayPin):
        pass

    def mock_cleanupGpio():
        pass

    monkeypatch.setattr(relay, "setGpioMode", mock_setGpioMode)
    monkeypatch.setattr(relay, "setupRelayPin", mock_setupRelayPin)
    monkeypatch.setattr(relay, "cleanupGpio", mock_cleanupGpio)

@pytest.fixture
def mock_relaySetHighLow(monkeypatch: pytest.MonkeyPatch):
    '''
    This is a fixture to mock setRelayPinHigh and setRelayPinLow, so that
    the relays IRL don't actually get triggered during testing.
    '''
    def mock_setRelayPinHigh(relayPin):
        global relayPinSetting, relayPinNumber
        relayPinSetting.append("High")
        relayPinNumber = relayPin

    def mock_setRelayPinLow(relayPin):
        global relayPinSetting, relayPinNumber
        relayPinSetting.append("Low")
        relayPinNumber = relayPin

    monkeypatch.setattr(relay, "setRelayPinHigh", mock_setRelayPinHigh)
    monkeypatch.setattr(relay, "setRelayPinLow", mock_setRelayPinLow)

def test_setRelay(mock_relaySetHighLow):
    '''
    This function tests that setRelay properly sets the relay pin to high or low
    depending on the inputs.
    '''
    global relayPinNumber, relayPinSetting
    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Set Relay High -------------------------------
    relay.setRelay(5, "High")
    assert relayPinSetting == ["High"]
    assert relayPinNumber == 5
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Set Relay Low --------------------------------
    relay.setRelay(10, "Low")
    assert relayPinSetting == ["Low"]
    assert relayPinNumber == 10
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

def test_toggleRelay1(mock_relaySetHighLow, mock_setup_cleanup):
    '''
    This functions tests that toggleRelay1 properly toggles the relay pin high,
    then to low, with the correct pin
    '''
    global relayPinNumber, relayPinSetting
    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay 1, 2 seconds --------------------
    relay.toggleRelay1(5, 2000, 1000)
    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 5
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay 1, 1 second, twice --------------
    relay.toggleRelay1(10, 1000, 1000)
    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 10
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

def test_toggleRelayGen(mock_relaySetHighLow, mock_setup_cleanup):
    '''
    This function tests that toggleRelayGen properly toggles the correct gen
    pin high and low once, based on the inputs
    '''
    global relayPinNumber, relayPinSetting
    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay General, Pin 20 Gen 1------------
    relay.toggleRelayGen(20, 2000, 1)
    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 20
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay General, Pin 25 Gen 2------------
    relay.toggleRelayGen(25, 2000, 2)
    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 25
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

def test_trigger_relay_one(mock_relaySetHighLow, mock_setup_cleanup):
    '''
    This test tests that trigger_relay_one is able to trigger the correct relay,
    be it the default or the general option, based on the input.
    '''
    global relayPinNumber, relayPinSetting
    relayPinNumber = 0
    relayPinSetting = []

    # To remember original value to set back later
    original_Relay_1 = relay.Relay_1
    original_GEN_OUT_1 = relay.GEN_OUT_1
    original_GEN_OUT_2 = relay.GEN_OUT_2
    original_GEN_OUT_3 = relay.GEN_OUT_3

    # setting Relay_1 to testing value
    relay.Relay_1 = 51
    relay.GEN_OUT_1 = 52
    relay.GEN_OUT_2 = 53
    relay.GEN_OUT_3 = 54

    # ------------- TEST SECTION: Trigger Relay 1, no TPO ----------------------
    relay.trigger_relay_one()

    time.sleep(5) # To allow threadpoolexecutor to finish task

    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 51
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Trigger Relay 1, TPO Gen 1 -------------------
    relay.trigger_relay_one("GEN_OUT_1")

    time.sleep(5) # To allow threadpoolexecutor to finish task

    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 52
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # Setting back original functions
    relay.Relay_1 = original_Relay_1
    relay.GEN_OUT_1 = original_GEN_OUT_1
    relay.GEN_OUT_2 = original_GEN_OUT_2
    relay.GEN_OUT_3 = original_GEN_OUT_3