import os
import sys
import pytest

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import relay

relayPinNumber = 0
relayPinSetting = ""

@pytest.fixture
def mock_relaySetHighLow(monkeypatch: pytest.MonkeyPatch):
    def mock_setRelayPinHigh(relayPin):
        global relayPinSetting, relayPinNumber
        relayPinSetting = "High"
        relayPinNumber = relayPin

    def mock_setRelayPinLow(relayPin):
        global relayPinSetting, relayPinNumber
        relayPinSetting = "Low"
        relayPinNumber = relayPin

    monkeypatch.setattr(relay, "setRelayPinHigh", mock_setRelayPinHigh)
    monkeypatch.setattr(relay, "setRelayPinLow", mock_setRelayPinLow)

def test_setRelay(mock_relaySetHighLow):
    relay.setRelay(5, "High")
    assert relayPinSetting == "High"
    assert relayPinNumber == 5

