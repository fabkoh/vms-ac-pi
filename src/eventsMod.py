import json
from datetime import datetime
import os

from executor import setup_logger, thread_pool_executor
from updateserver import update_server_events
import eventActionTriggerConstants
import eventActionTriggers
from lock import pending_logs_lock, archived_logs_lock, config_lock

path = os.path.dirname(os.path.abspath(__file__))

logger = setup_logger('EventsMod.log')


'''
    1. record_auth and record_button to record transLogs in archivedTrans.json and pendingTrans.json
'''

config = None
controllerSerial = None
MAX_JSON_LENGTH = None


def update_config():
    global config, controllerSerial, MAX_JSON_LENGTH

    with config_lock:
        f = open(path+'/json/config.json')
        config = json.load(f)
        f.close()

    controllerSerial = config['controllerConfig']['controllerSerialNo']
    MAX_JSON_LENGTH = int(config.get("archivedMAXlength", 10))


try:
    # max length before first half of jsons get deleted
    MAX_JSON_LENGTH = int(config["archivedMAXlength"])
except:
    MAX_JSON_LENGTH = 10

update_config()
'''
persondetails = {   "Name": personName,
                    "diffpassword" : [cardwiegandvalue,fingerwiegandvalue,pin], #everything besides the initial wiegand value used to identify personName  
                    "AccessGroup": AccessgroupName,
                    "Schedule": {
                                "2022-03-14":{"starttime":"18:00","endtime":"23:00"},
                                "2022-03-15": {"starttime":"18:00","endtime":"23:00"}
                                }
                }
authtype = e.g. card    Fingerprint,Pin

entrance =  e.g. MainDoor
status = e.g. In


dictionary 

direction  STRING
eventTime  DATETIME
person     PERSONID
entrance   ENTRANCEID
accessGroup   ACCESSGROUPID
eventActionType   EVENTACTIONTYPEID
controller         CONTROLLERID


'''

# updates pendingLogs.json and send to backend
# updates archivedLogs.json for backup


def record_auth_scans(name, accessGroup, authtype, entrance, status):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when auth_scan happens
    
        Parameters:
            name: ID of the person
            accessGroup: ID of the access group
            authtype: type of authentication used
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
    '''
    dictionary = {
        "person": {"personId": name},
        "accessGroup": {"accessGroupId": accessGroup},
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 1},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.AUTHENTICATED_SCAN, entrance)
    )
    
    update_logs_and_server(dictionary)

def invalid_pin_used(entrance, status):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when invalid pin is used

        Parameters:
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
    '''
    dictionary = {
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 14},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.UNAUTHENTICATED_SCAN, entrance)
    )

    update_logs_and_server(dictionary)


def pin_only_used(person_id, access_group_id, entrance, status):
    '''
    This functions creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when only pin is used

        Parameters:
            person_id: ID of the person
            access_group_id: ID of the access group
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
    '''
    dictionary = {
        "person": {"personId": person_id},
        "accessGroup": {"accessGroupId": access_group_id},
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 13},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.AUTHENTICATED_SCAN, entrance)
    )
    
    update_logs_and_server(dictionary)


def record_masterpassword_used(authtype, entrance, status):
    '''
    This functions creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when only pin is used

        Parameters:
            authtype: type of authentication used
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
    '''
    dictionary = {
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 2},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


def record_unauth_scans(authtype, entrance, status, name=None, access_group=None):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when unauth_scan happens
    
        Parameters:
            authtype: type of authentication used
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
            name: ID of the person
            accessGroup: ID of the access group
    '''
    dictionary = {
        "person": {"personId": name},
        "accessGroup": {"accessGroupId": access_group},
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 3},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.UNAUTHENTICATED_SCAN, entrance)
    )
    
    update_logs_and_server(dictionary)


def record_button_pressed(entrance, name_of_button):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when button is pressed

        Parameters:
            entrance: entrance ID
            name_of_button: name of the button pressed
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 9},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    
    e = entrance
    if e == '':  # no entrance assigned to this push button
        e = eventActionTriggerConstants.BOTH_ENTRANCE
    
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.EXIT_BUTTON_PRESSED, e)
    )

    update_logs_and_server(dictionary)


def fire_alarm_activated(gpio, level, tick):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when the fire alarm is activated
    '''
    entrance = ""
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 15},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    e = entrance
    if e == '':  # no entrance assigned to this push button
        e = eventActionTriggerConstants.BOTH_ENTRANCE
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.FIRE, e)
    )
    update_logs_and_server(dictionary)


def record_antipassback(authtype, entrance, status):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when antipassback occurred

        Parameters:
            authtype: type of authentication used
            entrance: entrance ID
            status: direction of the scan (IN or OUT)
    '''
    dictionary = {
        "direction": status, 
        "entrance": entrance, 
        "eventActionType": "ANTIPASSBACK : authenticated_scan ",
        "controller": controllerSerial, 
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


def record_mag_opened(entrance):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when magnetic contact at the door is opened
    with authentication

        Parameters:
            entrance: entrance ID
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 4},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(
        eventActionTriggerConstants.CONTACT_OPEN_WITH_AUTHENTICATION,
        eventActionTriggerConstants.START_TIMER,
        entrance))
    
    update_logs_and_server(dictionary)


def record_mag_closed(entrance):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when magnetic contact at the door is closed

        Parameters:
            entrance: entrance ID
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 5},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(
        eventActionTriggerConstants.CONTACT_OPEN_WITH_AUTHENTICATION,
        eventActionTriggerConstants.STOP_TIMER,
        entrance))
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(
        eventActionTriggerConstants.CONTACT_OPEN_WITHOUT_AUTHENTICATION,
        eventActionTriggerConstants.STOP_TIMER,
        entrance))
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_event(
        eventActionTriggerConstants.CONTACT_CLOSE, 
        entrance))
    update_logs_and_server(dictionary)


def record_mag_opened_warning(entrance):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server, and uses event_trigger_cb to trigger the output
    action for what should happen when magnetic contact at the door is opened
    without authentication

        Parameters:
            entrance: entrance ID
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 6},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(
        eventActionTriggerConstants.CONTACT_OPEN_WITHOUT_AUTHENTICATION,
        eventActionTriggerConstants.START_TIMER,
        entrance))

    update_logs_and_server(dictionary)


def record_buzzer_start(entrance):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server when the buzzer has started

    NOTE: This function is not used in the current implementation
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 7},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


def record_buzzer_end(entrance):
    '''
    This function creates a dictionary to send to backend using
    update_logs_and_server when the buzzer has stopped

    NOTE: This function is not used in the current implementation
    '''
    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 8},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


# update to update json files
def update_logs_and_server(dictionary):
    '''
    This function submits a task to the thread_pool_executor to update the
    respective log files, then update the server of the events with the
    pendingLogs.json file

        Parameters:
            dictionary: dictionary containing the event details
    '''
    def thread_task():
        update(path + "/json/archivedLogs.json", archived_logs_lock, dictionary)
        update(path + "/json/pendingLogs.json", pending_logs_lock, dictionary)

        update_server_events()

    # create thread to implement the above
    thread_pool_executor.submit(thread_task)


def update(file, lock, dictionary):
    '''
    This function opens and updates the json file with the dictionary provided
    by writing directly to it. If the file exceeds the MAX_JSON_LENGTH, the
    first half of the file will be deleted using clear_file_storage.

        Parameters:
            file: file to update
            lock: lock to prevent multiple threads from writing to the file
            at the same time
            dictionary: dictionary containing the event details
    '''
    # check if current json files exceed max length
    clear_file_storage(file, lock)
    # print("before lock", str(datetime.now()))

    with lock:
        with open(file, "r+") as outfile:
            try:
                data = json.load(outfile)
            except:
                data = []

            # print("before dict append", str(datetime.now()))

            data.append(dictionary)
            outfile.seek(0)
            # print("after dict append", str(datetime.now()))

            json.dump(data, outfile, indent=4)
    outfile.close()
    # print("after lock", str(datetime.now()))


# delete first half if exceeds length
def clear_file_storage(file, lock):
    '''
    This function checks if the json file exceeds the MAX_JSON_LENGTH, and
    deletes the first half of the file if it does

        Parameters:
            file: file to check
            lock: lock to prevent multiple threads from writing to the file
            at the same time
    '''
    with lock:
        with open(file, "r") as checkfile:
            try:
                checkdata = json.load(checkfile)
            except:
                checkdata = []

            if len(checkdata) > MAX_JSON_LENGTH:
                checkfile.close()
                with open(file, "w+") as outfile:
                    del checkdata[:(int(MAX_JSON_LENGTH/2))]
                    json.dump(checkdata, outfile, indent=4)
            else:
                checkfile.close()


def main():
    pass


if __name__ == "__main__":
    main()
