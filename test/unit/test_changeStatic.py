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

def test_change_static_ip(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that change_static_ip is able to properly change the static
    IP settings in the dhcpcd.conf file of the RPi. As we do not want the test
    to actually write to the .conf file, we have to mock a few things,
    including the readlines and writelines functions, along with the open
    function, so we have to create a MockFile class that is returned when open()
    is called.
    '''
    data_written = [] # List var to hold result from changeStatic
    
    # Setting up of mock functions and classes
    def mock_readlines():
        return ['#Configuration settings static IP:\n',
                '#interface eth0\n',
                '#static ip_address\n',
                '#static routers\n',
                '#static domain_name_servers\n']
    
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
    # Mocking restart_eth0 so that controller does not always restart connection
    def mock_restart_eth0():
        pass
    
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr(changeStatic, "restart_eth0", mock_restart_eth0)

    # Actual Testing Section
    changeStatic.change_static_ip('192.168.1.160', '192.168.1.254', '192.168.1.254')

    expected = ['#Configuration settings static IP:\n',
                'interface eth0\n',
                'static ip_address=192.168.1.160/24\n',
                'static routers=192.168.1.254\n',
                'static domain_name_servers=192.168.1.254\n']

    assert data_written == expected

def test_change_dhcp(monkeypatch: pytest.MonkeyPatch):
    '''
    This test tests that change_dhcp correctly comments out the static IP
    configuration lines in the dhcpcd.conf file of the RPi. As above, we are
    mocking the reading and writing of files, along with opening them, so that
    the actual .conf file is not changed during the test.
    '''
    data_written = [] # List var to hold result from changeStatic
    
    # Setting up of mock functions and classes
    def mock_readlines():
        return ['#Configuration settings static IP:\n',
                'interface eth0\n',
                'static ip_address=exampleIP\n',
                'static routers=exampleIP\n',
                'static domain_name_servers=exampleIP\n']
    
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
        
        def close(self):
            del self
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_open(filepath, mode):
        return MockFile(mode)
    # Mocking restart_eth0 so that controller does not always restart connection
    def mock_restart_eth0():
        pass
    
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr(changeStatic, "restart_eth0", mock_restart_eth0)

    # Actual Testing Section
    changeStatic.change_dhcp()

    expected = ['#Configuration settings static IP:\n',
                '# interface eth0\n',
                '# static ip_address=exampleIP\n',
                '# static routers=exampleIP\n',
                '# static domain_name_servers=exampleIP\n']
    
    assert data_written == expected
