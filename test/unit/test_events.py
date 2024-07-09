import os
import sys
import datetime

'''
This part is needed to be able to import the files from src for testing
'''
TEST_DIR = os.path.dirname(os.path.abspath(__file__)) # /vms-ac-pi/test/unit
SRC_DIR = os.path.abspath(os.path.join(os.path.join(TEST_DIR, os.pardir), os.pardir)) # /vms-ac-pi
sys.path.insert(0, SRC_DIR)

from src import events

def test_verify_datetime_day():
    '''
    This test tests that verify_datetime correctly returns true when the date is
    today
    '''
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")

    mock_json_contents = {
        today_string_formatted: [
            {
                "endtime": "24:00",
                "starttime": "00:00"
            }
        ]
    }

    assert events.verify_datetime(mock_json_contents)

def test_not_verify_datetime_day():
    '''
    This test tests that verify_datetime correctly returns false when the date 
    is tomorrow
    '''
    tomorrow_datetime = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_string_formatted = tomorrow_datetime.strftime("%Y-%m-%d")

    mock_json_contents = {
        tomorrow_string_formatted: [
            {
                "endtime": "24:00",
                "starttime": "00:00"
            }
        ]
    }

    assert not events.verify_datetime(mock_json_contents)

def test_verify_datetime_time():
    '''
    This test tests that verify_datetime correctly returns true when the data
    is today, and current time is within the timing schedule
    '''
    today_string_formatted = datetime.date.today().strftime("%Y-%m-%d")
    now = datetime.datetime.now()
    curr_hour = now.hour
    curr_min = now.min
    hour_before = f'{curr_hour - 1}:{curr_min}'
    hour_after = f'{curr_hour + 1}:{curr_min}'

    mock_json_contents = {
        today_string_formatted: [
            {
                "endtime": hour_after,
                "starttime": hour_before
            }
        ]
    }
    
    assert events.verify_datetime(mock_json_contents)