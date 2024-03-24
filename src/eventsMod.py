import json
from datetime import datetime
import os
import threading
from updateserver import update_server_events
import eventActionTriggerConstants
import eventActionTriggers
from lock import pending_logs_lock, archived_logs_lock, config_lock
from threading import Lock
import logging
# Create a logger
logger = logging.getLogger(__name__)

# Set the level of logging. It can be DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.DEBUG)

# Create a file handler for outputting log messages to a file
file_handler = logging.FileHandler('/home/etlas/logfileventsMod.log')

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

path = os.path.dirname(os.path.abspath(__file__))

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
    dictionary = {
        "person": {"personId": name},
        "accessGroup": {"accessGroupId": accessGroup},
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 1},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    logger.info("record auth scans, before event_trigger_cb")
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.AUTHENTICATED_SCAN, entrance)
    )
    logger.info("record auth scans, after event_trigger_cb")
    update_logs_and_server(dictionary)
    logger.info("record auth scans, after update_logs_and_server")

def invalid_pin_used(entrance, status):
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


def pin_only_used(entrance, status):
    dictionary = {
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 13},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    logger.info("record pin used, before event_trigger_cb")
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.AUTHENTICATED_SCAN, entrance)
    )
    logger.info("record pin used, after event_trigger_cb")
    update_logs_and_server(dictionary)
    logger.info("record pin used, after update_logs_and_server")
# updates pendingLogs.json and send to backend
# updates archivedLogs.json for backup


def record_masterpassword_used(authtype, entrance, status):
    dictionary = {
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 2},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)

# updates pendingTrans.json and send to backend
# updates archivedTrans.json for backup


def record_unauth_scans(authtype, entrance, status, name=None, access_group=None):
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
    print(f"Recorded unauth scan at {entrance}")
    update_logs_and_server(dictionary)


def record_button_pressed(entrance, name_of_button):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 9},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    e = entrance
    if e == '':  # no entrance assigned to this push button
        e = eventActionTriggerConstants.BOTH_ENTRANCE
    print(f"Recorded button pressed at {e}")
    logger.info("push button, before event_trigger_cb")
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.EXIT_BUTTON_PRESSED, e)
    )
    logger.info("push button, after event_trigger_cb")
    update_logs_and_server(dictionary)
    logger.info("push button, after update_logs_and_server")

# status = opened/ closed

def fire_alarm_activated(gpio, level, tick):
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
    print(f"Fire activated at {e}")
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.FIRE, e)
    )
    update_logs_and_server(dictionary)


def record_antipassback(authtype, entrance, status):

    dictionary = {
        "person": {"personId": name},
        "accessGroup": {"accessGroupId": accessGroup},
        "direction": status,
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 2},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    dictionary = {
        "direction": status, "entrance": entrance, "eventActionType": "ANTIPASSBACK : authenticated_scan ",
        "controller": controllerSerial, "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


def record_mag_opened(entrance):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 4},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(eventActionTriggerConstants.CONTACT_OPEN,
                                                                                        eventActionTriggerConstants.START_TIMER,
                                                                                        entrance))
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.CONTACT_OPEN_WITH_AUTHENTICATION, entrance)
    )
    update_logs_and_server(dictionary)


def record_mag_closed(entrance):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 5},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }
    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(eventActionTriggerConstants.CONTACT_OPEN,
                                                                                        eventActionTriggerConstants.STOP_TIMER,
                                                                                        entrance))
    update_logs_and_server(dictionary)


def record_mag_opened_warning(entrance):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 6},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    eventActionTriggers.event_trigger_cb(eventActionTriggerConstants.create_timer_event(eventActionTriggerConstants.CONTACT_OPEN,
                                                                                        eventActionTriggerConstants.START_TIMER,
                                                                                        entrance))
    eventActionTriggers.event_trigger_cb(
        eventActionTriggerConstants.create_event(
            eventActionTriggerConstants.CONTACT_OPEN_WITHOUT_AUTHENTICATION, entrance)
    )

    update_logs_and_server(dictionary)

# status = started buzzing/ stopped buzzing


def record_buzzer_start(entrance):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 7},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


def record_buzzer_end(entrance):

    dictionary = {
        "entrance": {"entranceId": entrance},
        "eventActionType": {"eventActionTypeId": 8},
        "controller": {"controllerSerialNo": controllerSerial},
        "eventTime": datetime.now().strftime(("%m-%d-%Y %H:%M:%S"))
    }

    update_logs_and_server(dictionary)


# update to update json files


def update_logs_and_server(dictionary):
    def thread_task():
        print("before update logs", str(datetime.now()))
        update(path + "/json/archivedLogs.json", archived_logs_lock, dictionary)
        update(path + "/json/pendingLogs.json", pending_logs_lock, dictionary)
        print("inside update_logs_and_server ", str(datetime.now()))

        update_server_events()

    # create thread to implement the above 
    thread = threading.Thread(target=thread_task)
    thread.start()


def update(file, lock, dictionary):
    # check if current json files exceed max length
    clear_file_storage(file, lock)
    print("before lock", str(datetime.now()))

    with lock:
        with open(file, "r+") as outfile:
            try:
                data = json.load(outfile)
            except:
                data = []

            print("before dict append", str(datetime.now()))

            data.append(dictionary)
            outfile.seek(0)
            print("after dict append", str(datetime.now()))

            json.dump(data, outfile, indent=4)
    outfile.close()
    print("after lock", str(datetime.now()))



# delete first half if exceeds length
def clear_file_storage(file, lock):
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
    # persondetails = {"Name": "YongNing","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}

    # record_auth_scans(persondetails,"Card","Maindoor","In")
    # record_button_pressed("Maindoor","Security guard button")

    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    pass


if __name__ == "__main__":
    main()
