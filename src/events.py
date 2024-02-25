
import asyncio
from datetime import datetime, date
# from GPIOconfig import Gen_Out_1

import relay
import eventsMod
import json
import time
import updateserver
import os
path = os.path.dirname(os.path.abspath(__file__))

'''
    1. contains class Timer 
    2. check_for_wiegand
    3. bits_reader
'''

# config
# DO NOT CHANGE THE BELOW VALUES, the spring code generates the same names for comparison purposes
# name of types in credTypeDescriptions
pin_type = "Pin"
face_type = "Face"
card_type = "Card"
fingerprint_type = "Fingerprint"
and_delimiter = " + "
or_delimiter = " / "

# bits value passed to reader_detect_bits by wiegand reader (decoder class)
pin_bits = 4  # 1 pin number
card_bits = 26
# end config


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            print("Timer is running. Use .stop() to stop it")
            return
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            print("Timer is not running. Use .start() to start it")
            return
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")

    def check(self, TIME):
        """return True if current_elapsed_time exceeds TIME"""
        if self._start_time is None:
            print("Timer is not running. Use .start() to start it")
            return

        current_elapsed_time = time.perf_counter() - self._start_time
        if current_elapsed_time > TIME:
            return True

        return False

    def status(self):
        """return True if timing has started"""
        if self._start_time:
            return True
        return False


config = None
GPIOpins = None
TIMEOUT = None
E1 = None
E2 = None

Gen_Out_1 = None
E1_Mag = None
E1_Button = None

E2_Mag = None
E2_Button = None

DEFAULT_CRED_TIMEOUT = 20
DEFAULT_MAG_TIMEOUT = 10
DEFAULT_BUZZER_TIMEOUT = 10

CRED_TIMEOUT_E1 = None
CRED_TIMEOUT_E2 = None
MAG_TIMEOUT_E1 = None
MAG_TIMEOUT_E2 = None
BUZZER_TIMEOUT_E1 = None
BUZZER_TIMEOUT_E2 = None


def update_config():
    '''Call this before events.update_credOccur'''
    global config, GPIOpins, E1, E2, E1_Mag, Gen_Out_1, E1_Button, E2_Mag, E2_Button, TIMEOUT, \
        CRED_TIMEOUT_E1, CRED_TIMEOUT_E2, MAG_TIMEOUT_E1, MAG_TIMEOUT_E2, BUZZER_TIMEOUT_E1, BUZZER_TIMEOUT_E2
    f = open(path+'/json/config.json')
    config = json.load(f)
    f.close()

    E1 = config["EntranceName"]["E1"]
    E2 = config["EntranceName"]["E2"]

    GPIOpins = config["GPIOpins"]
    TIMEOUT = config["TIMEOUT"]

    Gen_Out_1 = int(GPIOpins["Gen_Out_1"])
    E1_Mag = int(GPIOpins["E1_Mag"])
    E1_Button = int(GPIOpins["E1_Button"])

    E2_Mag = int(GPIOpins["E2_Mag"])
    E2_Button = int(GPIOpins["E2_Button"])

    CRED_TIMEOUT_E1 = int(TIMEOUT.get("CRED_TIMEOUT_E1", DEFAULT_CRED_TIMEOUT))
    CRED_TIMEOUT_E2 = int(TIMEOUT.get("CRED_TIMEOUT_E2", DEFAULT_CRED_TIMEOUT))
    MAG_TIMEOUT_E1 = int(TIMEOUT.get("MAG_TIMEOUT_E1", DEFAULT_MAG_TIMEOUT))
    MAG_TIMEOUT_E2 = int(TIMEOUT.get("MAG_TIMEOUT_E2", DEFAULT_MAG_TIMEOUT))
    BUZZER_TIMEOUT_E1 = int(TIMEOUT.get(
        "BUZZER_TIMEOUT_E1", DEFAULT_BUZZER_TIMEOUT))
    BUZZER_TIMEOUT_E2 = int(TIMEOUT.get(
        "BUZZRE_TIMEOUT_E2", DEFAULT_BUZZER_TIMEOUT))

    check_entrance_status()


credOccur = None

E1_entrance_schedule = ""
E1_thirdPartyOption = "N.A."
E2_entrance_schedule = ""
E2_thirdPartyOption = "N.A."


def verify_datetime(schedule):

    try:
        for scheduledate, scheduletime in schedule.items():
            # print(scheduledate,scheduletime)
            if scheduledate == str(date.today()):
                # print("today in schedule")
                for timing in scheduletime:
                    now = datetime.now().time()
                    start = datetime.strptime(
                        timing["starttime"], "%H:%M").time()
                    if timing["endtime"] != "24:00":
                        end = datetime.strptime(
                            timing["endtime"], "%H:%M").time()

                        if now >= start and now < end:
                            # print("now in schedule") # strictly within
                            return True
                    else:
                        if now >= start:
                            # print("now in schedule") # strictly within
                            return True
    except:
        pass

    return False


def check_entrance_status():

    if verify_datetime(E1_entrance_schedule):
        # print("unlock E1")
        relay.lock_unlock_entrance_one(E1_thirdPartyOption, True)
    else:
        # print("lock E1")
        relay.lock_unlock_entrance_one(E1_thirdPartyOption, False)

    if verify_datetime(E2_entrance_schedule):
        # print("unlock E2")
        relay.lock_unlock_entrance_two(E2_thirdPartyOption, True)
    else:
        # print("lock E2")
        relay.lock_unlock_entrance_two(E2_thirdPartyOption, False)


def update_credOccur():
    '''Call this after events.update_config'''
    global credOccur, E1_entrance_schedule, E2_entrance_schedule, E1_thirdPartyOption, E2_thirdPartyOption
    f = open(path+'/json/credOccur.json')
    credOccur = json.load(f)
    f.close()
    for entrance in credOccur:
        if entrance["Entrance"] == E1:
            E1_entrance_schedule = entrance["EntranceSchedule"]
            E1_thirdPartyOption = entrance["ThirdPartyOptions"]

        if entrance["Entrance"] == E2:

            E2_entrance_schedule = entrance["EntranceSchedule"]
            E2_thirdPartyOption = entrance["ThirdPartyOptions"]


# initialise
update_config()
update_credOccur()
check_entrance_status()

mag_E1_allowed_to_open = False
mag_E2_allowed_to_open = False

timeout_cred_E1_IN = Timer()
timeout_cred_E1_OUT = Timer()
timeout_mag_E1 = Timer()
timeout_buzzer_E1 = Timer()

timeout_cred_E2_IN = Timer()
timeout_cred_E2_OUT = Timer()
timeout_mag_E2 = Timer()
timeout_buzzer_E2 = Timer()

MAX_PIN_LENGTH = 6

credentials_E1_IN = {}  # dict to store credentials
credentials_E1_OUT = {}  # dict to store credentials
credentials_E2_IN = {}  # dict to store credentials
credentials_E2_OUT = {}  # dict to store credentials

pinsvalue_E1_IN = []  # array to store pins
pinsvalue_E1_OUT = []  # array to store pins
pinsvalue_E2_IN = []  # array to store pins
pinsvalue_E2_OUT = []  # array to store pins


# takes in string wiegand value, return name, passwords, accessgroup and schedule
def check_for_wiegand(value):
    for entranceslist in credOccur:
        Accessgroups = entranceslist["EntranceDetails"]["AccessGroups"]
        for specificAccessGroup in Accessgroups:
            for groupName, groupdetails in specificAccessGroup.items():
                for persondetails in groupdetails["Persons"]:

                    diffpassword = list()
                    authmethod = None

                    # check wiegand value belongs to which person, add the rest of wiegand values and pins to diffpassowrd
                    for type, password in persondetails["Credentials"].items():
                        if value == password:
                            authmethod = type
                            personName = persondetails["Name"]

                        if type != authmethod:
                            diffpassword.append(password)

                    # once done, return the data
                    if authmethod:
                        return {"Name": personName, "diffpassword": diffpassword, "AccessGroup": groupName, "Schedule": groupdetails["Schedule"]}


def open_door(entrance_prefix):
    '''Helper function for eventActionTriggers.py

    Args:
    entrance_prefix(string): "E1" | "E2"
    '''
    global mag_E1_allowed_to_open, mag_E2_allowed_to_open
    if entrance_prefix == "E1":
        mag_E1_allowed_to_open = True
        relay.trigger_relay_one(E1_thirdPartyOption)
    elif entrance_prefix == "E2":
        mag_E2_allowed_to_open = True
        relay.trigger_relay_two(E2_thirdPartyOption)


def open_door_using_entrance_id(entrance_id):
    '''same as open_door (see above) but with entrance_id
       Does nothing if entrance_id is not the same as in config.json

       entrance_id (int): entrance id
    '''
    # print("here",config.get("EntranceName",{}).get("E1",None) == entrance_id)
    if entrance_id and entrance_id == config.get("EntranceName", {}).get("E1", None):
        # print("here")
        open_door("E1")
    elif entrance_id and entrance_id == config.get("EntranceName", {}).get("E2", None):
        open_door("E2")

# Events Management: Output actions timer for GENOUT_1/2/3


def open_GEN_OUT(GEN_OUT_PIN, timer, GenNo):
    relay.open_GEN_OUT(GEN_OUT_PIN, timer, GenNo)

# keep track of wiegand values and pins
# check if person allowed to enter
# trigger relays
# record Trans
# TODO: add event logging


def reader_detects_bits(bits, value, entrance):

    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    temp = entrance.split("_")
    entrance_prefix = temp[0]
    entrancename = config["EntranceName"][entrance_prefix]
    # if entrance not found
    entrance_direction = temp[1]

    # timeout_cred is timer
    # cred_timeout is time limit
    if entrance == "E1_IN":
        credentials = credentials_E1_IN
        pinsvalue = pinsvalue_E1_IN
        timeout_cred = timeout_cred_E1_IN  # this is timer
        cred_timeout = CRED_TIMEOUT_E1

    if entrance == "E1_OUT":
        credentials = credentials_E1_OUT
        pinsvalue = pinsvalue_E1_OUT
        timeout_cred = timeout_cred_E1_OUT
        cred_timeout = CRED_TIMEOUT_E1

    if entrance == "E2_IN":
        credentials = credentials_E2_IN
        pinsvalue = pinsvalue_E2_IN
        timeout_cred = timeout_cred_E2_IN
        cred_timeout = CRED_TIMEOUT_E2

    if entrance == "E2_OUT":
        credentials = credentials_E2_OUT
        pinsvalue = pinsvalue_E2_OUT
        timeout_cred = timeout_cred_E2_OUT
        cred_timeout = CRED_TIMEOUT_E2

    # helper functions
    def reset_cred_and_stop_timer():
        '''resets credentials and pin values and stops timer

        Returns None'''
        # add unauth scan function call
        # print(f"recording {auth_method_name} at {entrancename}")
        # eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction,  "", list(access_group.keys())[0])
        
        pinsvalue.clear()
        credentials.clear()
        if timeout_cred.status():
            timeout_cred.stop()


    def greenlight_and_beep():
        '''set wiegand reader to show green light and give a recognisaible beep, 2-3 secondas long'''
        if entrance_prefix == "E1":
            pass

    def open_door():
        '''opens the door, set mags to allow open, update server events'''
        # print("open")
        global mag_E1_allowed_to_open
        global mag_E2_allowed_to_open
        if entrance_prefix == "E1":
            mag_E1_allowed_to_open = True
            relay.trigger_relay_one(E1_thirdPartyOption)
        elif entrance_prefix == "E2":
            mag_E2_allowed_to_open = True
            relay.trigger_relay_two(E2_thirdPartyOption)

    # steps
    # 1 start / restart timer
    # 2 gather credentials
    # 3 check credentials
    # 4 follow up actions (open door, logs etc)

    # start / restart timer
    # if expired => clear cred and refresh timer
    # if not started => start
    # else do nothing
    if timeout_cred.status():
        if timeout_cred.check(cred_timeout):
            reset_cred_and_stop_timer()
            timeout_cred.start()
    else:
        timeout_cred.start()

    # gather credentials
    credential_added = False
    if bits == pin_bits:  # 1 number keyed in
        print("bits={} value={}".format(bits, value))
        if 0 <= value <= 9:  # normal input
            if len(pinsvalue) > MAX_PIN_LENGTH:
                return
            pinsvalue.append(str(value))
        elif value == 10:  # clear input
            pinsvalue.clear()
        elif value == 11:  # submit
            if pinsvalue:
                credentials[pin_type] = ''.join(pinsvalue)
                pinsvalue.clear()
                credential_added = True
    elif bits == card_bits:  # card
        credentials[card_type] = "0"+str(int("{:026b}".format(value)[1:25], 2))
        print("bits={} value={}".format(
            bits, "0"+str(int("{:026b}".format(value)[1:25], 2))))
        credential_added = True

    # checking for creds
    # 1 check master password
    # 2 check auth method (if cred entered not in curr cred schedule, reset)
    # 3 check person creds
    if credential_added:
        print("check credentials")
        print(credentials)
        try:
            device_details = {}
            entrance_details = {}
            for entrance_list in credOccur:
                if "Entrance" in entrance_list and entrance_list["Entrance"] == entrancename:
                    entrance_details = entrance_list.get("EntranceDetails", {})
                    device_details = entrance_details.get(
                        "AuthenticationDevices", {}).get(entrance_direction, {})
            if entrance_details == {}:  # entrance not found, quit
                eventsMod.record_unauth_scans(None, None, entrance_direction)
                return

            # check master password
            if pin_type in credentials and \
               "Masterpassword" in device_details and \
               credentials[pin_type] == device_details["Masterpassword"]:
                print("masterpassword used")
                eventsMod.record_masterpassword_used(
                    "Master Pin", entrancename, entrance_direction)
                open_door()
                reset_cred_and_stop_timer()
                # eventsMod.record_masterpassword_used("masterpassword", entrancename, entrance_direction)
                # updateserver.update_server_events()
                return

            # check auth method
            # print(device_details)
            auth_method_name = device_details["defaultAuthMethod"]
            for auth_method in device_details.get("AuthMethod", []):
                if "Method" in auth_method and \
                   verify_datetime(auth_method.get("Schedule", {})):
                    auth_method_name = auth_method["Method"]
                    break

            auth_method_is_and = and_delimiter in auth_method_name
            auth_method_keys = auth_method_name.split(
                and_delimiter) if auth_method_is_and else auth_method_name.split(or_delimiter)
            print("auth_method_is_and, auth_method_keys",
                  auth_method_is_and, auth_method_keys)

            # check for credentials not in auth_method_keys
            if any(map(lambda k: k not in auth_method_keys, credentials)):
                print("auth method not allowed at this timing ")
                eventsMod.record_unauth_scans(
                    auth_method_name, entrancename, entrance_direction)
                reset_cred_and_stop_timer()
                return
            
            # have some crendetials but need more
            if ((auth_method_is_and and any(map(lambda k: k in credentials, auth_method_keys)))
                    and not all(map(lambda k: k in credentials, auth_method_keys))):
                print("requires more credentials")
                eventsMod.record_unauth_scans(
                    auth_method_name, entrancename, entrance_direction)
                return
            
            # check if need to check if cred belongs to someone
            if ((auth_method_is_and and all(map(lambda k: k in credentials, auth_method_keys))) or  # AND, all auth methods present
               ((not auth_method_is_and) and any(map(lambda k: k in credentials, auth_method_keys)))):  # OR, 1 auth method present
                # check person cred
                # 1 find the person
                # 2 check if the person's access group can enter
                print("trying to find person")
                for access_group in entrance_details.get("AccessGroups", []):
                    # find the person
                    person_found = False
                    access_group_info = list(access_group.values())[0] if type(
                        access_group) is dict and len(access_group) > 0 else {}
                    for person in access_group_info.get("Persons", []):
                        # check if this person has the creds
                        person_credentials = person.get("Credentials", {})
                        # print(person_credentials)
                        # print("person_credentials",person_credentials)
                        # print("credentials",credentials)

                        def checkcred(k):
                            listOfCred = person_credentials.get(k[0])
                            if listOfCred is None:
                                return False
                            for singleCred in listOfCred:
                                if singleCred.get("Value") == k[1]:
                                    print(datetime.now().date() <= datetime.strptime(
                                        singleCred.get("EndDate"), '%Y-%m-%d').date())
                                    if singleCred.get("IsPerm"):
                                        return True

                                    return datetime.now().date() <= datetime.strptime(singleCred.get("EndDate"), '%Y-%m-%d').date()

                            return False
                        # k[0] refers to credType, k[1] refers to value of corresponding cred
                        # see if all credentials belong to person
                        if all(map(checkcred, list(credentials.items()))):
                            # check if the person's access group can enter
                            # print(verify_datetime(access_group_info.get('Schedule', {})))
                            if verify_datetime(access_group_info.get('Schedule', {})):

                                # auth scan
                                print("found person, allowed to enter",
                                      auth_method_name, type(auth_method_name))
                                print(auth_method_name)
                                if "Pin" == auth_method_name:
                                    eventsMod.pin_only_used(
                                        entrancename, entrance_direction)
                                else:
                                    eventsMod.record_auth_scans(person.get("Name", ""), list(access_group.keys())[
                                                                0], auth_method_name, entrancename, entrance_direction)
                                open_door()
                                # set weigand reader to show green light and give a recognisaible beep, 2-3 secondas song
                                

                                reset_cred_and_stop_timer()
                                return
                            # person dont have access at this time
                            print(
                                "found person, but not allowed to enter at this timing")
                            if "Pin" == auth_method_name:
                                eventsMod.invalid_pin_used(
                                    entrancename, entrance_direction)
                            else:
                                eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction, person.get(
                                    "Name", ""), list(access_group.keys())[0])
                            reset_cred_and_stop_timer()
                            return
                # cannot find person
                print("cannot find person")
                if "Pin" == auth_method_name:
                    eventsMod.invalid_pin_used(
                        entrancename, entrance_direction)
                else:
                    eventsMod.record_unauth_scans(
                        auth_method_name, entrancename, entrance_direction)
                reset_cred_and_stop_timer()
                return

        except Exception as e:
            print("cannot check cred", str(e))
            pass

    return


def check_for_masterpassword(credentials, entrancename, entrance_direction):
    for entranceslist in credOccur:
        if entranceslist["Entrance"] == entrancename:
            for devicenumber, devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
                if devicedetails["Direction"] == entrance_direction:
                    if credentials[0] == devicedetails["Masterpassword"]:
                        return True
    return False

# take in verifydetails("MainDoor","In") return auth type


def verify_authtype(entrance, device):
    # for data in list of entrances
    for entranceslist in credOccur:
        if entranceslist["Entrance"] == entrance:
            for devicenumber, devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
                if devicedetails["Direction"] == device:
                    for methoddict in devicedetails["AuthMethod"]:
                        # check which authtype is activated for that particular schedule
                        if verify_datetime(methoddict["Schedule"]):
                            return methoddict["Method"]


'''
returns True if current moment is in schedule
schedule = {
                "2022-03-14":{"starttime":"18:00","endtime":"23:00"},
                "2022-03-15": {"starttime":"18:00","endtime":"23:00"}
              }
'''
'''
def verify_datetime(schedule):
    #print(schedule)
    #print(type(schedule))
    #print(str(date.today()))
    print(datetime.now())
    for scheduledate,scheduletime in schedule.items():
        #print(scheduledate,scheduletime)
        if scheduledate == str(date.today()):
            print("today in schedule")
            for timing in scheduletime:
                now = datetime.now().time()
                start = datetime.strptime(timing["starttime"], "%H:%M").time()
                if timing["endtime"] != "24:00":
                    end = datetime.strptime(timing["endtime"], "%H:%M").time()
                        
                    if now >= start and now < end:
                        print("now in schedule") # strictly within
                        return True
                else:
                    if now >= start:
                        print("now in schedule") # strictly within
                        return True

    return False 
'''

# check if person has entered the zone
# entrance = e.g. "E1R1"
# - if In
# 	- if person inside local jsons, not allowed to enter
# 	- if person not inside local jsons, allowed to enter, add to json
# - if out
# 	- if person inside local json, allowed to leave and remove from json
# 	- if person not inside local json, not allowed to leave


def verify_zone_status(entrance, entrancestatus, persondetails):
    filename = "json/" + "status.json"
    with open(filename, "r") as checkfile:
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata = {entrance[:2]: []}

        if entrancestatus == "IN":  # check if person inside
            try:

                for person in checkdata[entrance[:2]]:
                    name = person["Name"]
                    accessgroup = person["AccessGroup"]
                    if persondetails['Name'] == name and persondetails["AccessGroup"] == accessgroup:
                        return False
            except:
                pass
            return True

        elif entrancestatus == "OUT":
            try:
                for person in checkdata[entrance[:2]]:
                    name = person["Name"]
                    accessgroup = person["AccessGroup"]
                    if persondetails['Name'] == name and persondetails["AccessGroup"] == accessgroup:
                        return True
            except:
                pass
            return False

    return False


def update_zone_status(entrance, entrancestatus, persondetails):

    filename = "json/"+"status.json"
    with open(filename, "r") as checkfile:
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata = {"controllerId": "", "E1": [], "E2": []}

    # print(verify_zone_status(entrance,entrancestatus,persondetails))
    if verify_zone_status(entrance, entrancestatus, persondetails):
        controllerId = config["controllerConfig"][0]["controllerId"]
        dictionary = {"Name": persondetails["Name"],
                      "AccessGroup": persondetails["AccessGroup"]}
        with open(filename, "w+") as outfile:
            updateserver.update_external_zone_status(
                controllerId, entrance[:2], dictionary, entrancestatus)

            if entrancestatus == "In":
                checkdata[entrance[:2]].append(dictionary)
                json.dump(checkdata, outfile, indent=4)

            elif entrancestatus == "Out":
                for person in checkdata[entrance[:2]]:
                    if persondetails['Name'] == person["Name"] and persondetails["AccessGroup"] == person["AccessGroup"]:
                        checkdata[entrance[:2]].remove(person)
                json.dump(checkdata, outfile, indent=4)


# persondetails = {"Name": "Bryan","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}
# print(verify_zone_status("E1R1","In",persondetails))
# update_zone_status("E1R1","In",persondetails)

# check if antipassback if required
def verify_antipassback(entrancename):
    # read from credOccur.json
    for entrancelist in credOccur:
        if entrancelist["Entrance"] == entrancename:
            if entrancelist["EntranceDetails"]["Antipassback"] == "Yes":
                return True

    return False


def gen_check(gpio):
    if gpio == Gen_Out_1:
        print("Gen out 1 ")


debounce_delay = 0.05 # 50ms debounce delay


def mag_detects_rising(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open


    if time.time() - mag_detects_rising.last_call_time < debounce_delay:
        return

    if gpio == E1_Mag:
        timeout_mag_E1.start()
        print(f"{E1} is opened at " + str(datetime.now()))
        if mag_E1_allowed_to_open:
            eventsMod.record_mag_opened(E1)
        else:
            eventsMod.record_mag_opened_warning(E1)
        updateserver.update_server_events()

    if gpio == E2_Mag:
        timeout_mag_E2.start()
        print(f"{E2} is opened at " + str(datetime.now()))
        if mag_E2_allowed_to_open:
            eventsMod.record_mag_opened(E2)
        else:
            eventsMod.record_mag_opened_warning(E2)
        updateserver.update_server_events()

    mag_detects_rising.last_call_time = time.time()

mag_detects_rising.last_call_time = 0

def mag_detects_falling(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    if time.time() - mag_detects_falling.last_call_time < debounce_delay:
        return

    if gpio == E1_Mag:
        timeout_mag_E1.stop()
        print(f"{E1} is closed at " + str(datetime.now()))
        mag_E1_allowed_to_open = False
        eventsMod.record_mag_closed(E1)
        updateserver.update_server_events()

    if gpio == E2_Mag:
        timeout_mag_E2.stop()
        print(f"{E2} is closed at " + str(datetime.now()))
        mag_E2_allowed_to_open = False
        eventsMod.record_mag_closed(E2)
        updateserver.update_server_events()

    mag_detects_falling.last_call_time = time.time()

mag_detects_falling.last_call_time = 0


def button_detects_change(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    # debounce logic
    if time.time() - button_detects_change.last_call_time < debounce_delay:
        return

    # handle button press
    if gpio == E1_Button:
        print(f"{E1} push button1 is pressed at " + str(datetime.now()))
        mag_E1_allowed_to_open = True
        relay.trigger_relay_one(E1_thirdPartyOption)
        eventsMod.record_button_pressed(E1, "Security Guard Button")

    elif gpio == E2_Button:
        print(f"{E2} push button2 is pressed at " + str(datetime.now()))
        mag_E2_allowed_to_open = True
        relay.trigger_relay_two(E2_thirdPartyOption)
        eventsMod.record_button_pressed(E2, "Security Guard Button")

    # update last call time
    button_detects_change.last_call_time = time.time()

# initialize the last call time
button_detects_change.last_call_time = 0

# def button_detects_change(gpio, level, tick):
#     global mag_E1_allowed_to_open
#     global mag_E2_allowed_to_open

#     if gpio == E1_Button:
#         print(f"{E1} push button1 is pressed at " + str(datetime.now()))
#         mag_E1_allowed_to_open = True
#         relay.trigger_relay_one(E1_thirdPartyOption)
#         eventsMod.record_button_pressed(E1, "Security Guard Button")

#     if gpio == E2_Button:
#         print(f"{E2} push button2 is pressed at " + str(datetime.now()))
#         mag_E2_allowed_to_open = True
#         relay.trigger_relay_two(E2_thirdPartyOption)
#         eventsMod.record_button_pressed(E2, "Security Guard Button")


# 1st person going in
# reader_detects_bits(26,"s1e97ncksiu","E1_IN")
# bits_reader(26,"696955874","E1R1")

# 2nd person going in
# bits_reader(26,"2535645","E1R1")
# bits_reader(26,"ege56g4er","E1R1")

# 2nd person going in AGAIN
# bits_reader(26,"2535645","E1R1")
# bits_reader(26,"ege56g4er","E1R1")

# 1st person going out
# bits_reader(26,"s1e97ncksiu","E1R2")
# bits_reader(26,"696955874","E1R2")
