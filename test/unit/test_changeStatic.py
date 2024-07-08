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

    def mock_readlines(self):
        return ['interface eth0',
                'static ip line',
                'static routers line',
                'static dns line']
    
    def mock_writelines(self, data):
        nonlocal data_written
        data_written = data
    
    class MockFile:
        def __init__(self, mode):
            self.mode = mode
        
        def writelines(self, data):
            return mock_writelines(self, data)
        
        def readlines(self):
            return mock_readlines(self)
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_open(filepath, mode):
        return MockFile(mode)
    
    monkeypatch.setattr("builtins.open", mock_open)

    changeStatic.change_static_ip('test_ip_address.250', 'test_router198', 'test_dns8888')

    print(data_written)
    # data_extracted = []
    # def mock_writelines(self, data):
    #     nonlocal data_extracted
    #     data_extracted = data
    # def mock_restart_eth0():
    #     pass
    # monkeypatch.setattr(_io.TextIOWrapper, "writelines", mock_writelines)
    # monkeypatch.setattr(changeStatic, "restart_eth0", mock_restart_eth0)

    # changeStatic.change_static_ip('test_ip_address.250', 'test_router198', 'test_dns8888')

    # print(data_extracted)


