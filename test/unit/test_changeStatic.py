import os
import sys
import pytest

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import changeStatic
import io # needed to mock writelines

def test_change_static_ip(monkeypatch: pytest.MonkeyPatch):
    data_extracted = []
    def mock_writelines(self, data):
        nonlocal data_extracted
        data_extracted = data
    def mock_restart_eth0():
        pass
    # monkeypatch.setattr(_io.TextIOWrapper, "writelines", mock_writelines)
    monkeypatch.setattr(changeStatic, "restart_eth0", mock_restart_eth0)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: mock_file)
    mock_file = type("MockFile", (object,), {"writelines": mock_writelines, "__enter__": lambda s: s, "__exit__": lambda s, t, v, tb: None})()

    changeStatic.change_static_ip('test_ip_address.250', 'test_router198', 'test_dns8888')

    print(data_extracted)


