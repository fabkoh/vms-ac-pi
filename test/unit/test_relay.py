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
    global relayPinNumber, relayPinSetting

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay 1, 2 seconds --------------------
    relay.toggleRelay1(5, 2000, 1000, 1)
    assert relayPinSetting == ["High", "Low"]
    assert relayPinNumber == 5
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

    # ------------- TEST SECTION: Toggle Relay 1, 1 second, twice --------------
    relay.toggleRelay1(10, 1000, 1000, 2)
    assert relayPinSetting == ["High", "Low", "High", "Low"]
    assert relayPinNumber == 10
    # ------------- END OF TEST SECTION ----------------------------------------

    relayPinNumber = 0
    relayPinSetting = []

def test_toggleRelayGen(mock_relaySetHighLow, mock_setup_cleanup):
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