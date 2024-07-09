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
    data_written = []

    def mock_readlines():
        return ['#Configuration settings static IP:\n',
                'interface eth0\n',
                'static ip_address\n',
                'static routers\n',
                'static domain_name_servers\n']
    
    def mock_writelines(data):
        nonlocal data_written
        data_written = data
    
    class MockFile:
        def __init__(self, mode):
            self.mode = mode
        
        def writelines(self, data):
            return mock_writelines(data)
        
        def readlines(self):
            return mock_readlines()
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_open(filepath, mode):
        return MockFile(mode)
    def mock_restart_eth0():
        pass
    
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr(changeStatic, "restart_eth0", mock_restart_eth0)

    changeStatic.change_static_ip('192.168.1.160', '192.168.1.254', '192.168.1.254')

    expected = ['#Configuration settings static IP:\n',
                'interface eth0\n',
                'static ip_address=192.168.1.160/24\n',
                'static routers=192.168.1.254\n',
                'static domain_name_servers=192.168.1.254\n']

    assert data_written == expected
