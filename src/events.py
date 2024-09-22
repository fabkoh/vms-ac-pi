from datetime import datetime, date, timedelta
from dateutil.rrule import rrulestr

from executor import setup_logger
import relay
import eventsMod
import json
import time
import updateserver
import os
from dateutil.rrule import rrulestr
from dateutil.tz import tzlocal

from lock import config_lock
import GPIOconfig

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
fingerprint_type = "FingerPrint"
and_delimiter = " + "
or_delimiter = " / "

# bits value passed to reader_detect_bits by wiegand reader (decoder class)
pin_bits = 4  # 1 pin number
card_bits = 26
# end config

logger = setup_logger('Events.log')


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            # print("Timer is running. Use .stop() to stop it")
            return
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            # print("Timer is not running. Use .start() to start it")
            return
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        # print(f"Elapsed time: {elapsed_time:0.4f} seconds")

    def check(self, TIME):
        """return True if current_elapsed_time exceeds TIME"""
        if self._start_time is None:
            # print("Timer is not running. Use .start() to start it")
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
    with config_lock:
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
    if "rrule" in schedule and "starttime" in schedule and "endtime" in schedule:
        # print("before verify datetime: ", datetime.now())
        try:
            rule = rrulestr(schedule["rrule"])
            
            # Get the current time with local timezone
            now = datetime.now(tzlocal())
            
            # Parse the start and end times as naive times
            start_time = datetime.strptime(schedule["starttime"], "%H:%M").time()
            if schedule["endtime"] == "24:00":
                end_time = datetime.strptime("23:59:59", "%H:%M:%S").time()
            else:
                end_time = datetime.strptime(schedule["endtime"], "%H:%M").time()

            # Adjust 'now' to yesterday to ensure today's occurrences are included
            yesterday = now - timedelta(days=1)
            next_occurrence = rule.after(yesterday, inc=True)
            # print(next_occurrence.date(), now.date())
            # Check if the next occurrence is today and within the time range
            if next_occurrence.date() == now.date():
                # print(start_time, now.time(), end_time)
                if start_time <= now.time() <= end_time:
                    return True
            return False
        except Exception as e:
            print(e)
    
    return False
  
    try:
        for scheduledate, scheduletime in schedule.items():
            # # print(scheduledate,scheduletime)
            if scheduledate == str(date.today()):
                # # print("today in schedule")
                for timing in scheduletime:
                    now = datetime.now().time()
                    start = datetime.strptime(
                        timing["starttime"], "%H:%M").time()
                    if timing["endtime"] != "24:00":
                        end = datetime.strptime(
                            timing["endtime"], "%H:%M").time()

                        if now >= start and now < end:
                            # # print("now in schedule") # strictly within
                            return True
                    else:
                        if now >= start:
                            # # print("now in schedule") # strictly within
                            return True
    except:
        pass

    return False


def check_entrance_status():
    '''
    This function checks for whether the different entrances are within
    schedule, and then physically calls the relays to lock or unlock the
    entrances accordingly.
    '''
    if verify_datetime(E1_entrance_schedule):
        # # print("unlock E1")
        relay.lock_unlock_entrance_one(E1_thirdPartyOption, True)
    else:
        # # print("lock E1")
        relay.lock_unlock_entrance_one(E1_thirdPartyOption, False)

    if verify_datetime(E2_entrance_schedule):
        # # print("unlock E2")
        relay.lock_unlock_entrance_two(E2_thirdPartyOption, True)
    else:
        # # print("lock E2")
        relay.lock_unlock_entrance_two(E2_thirdPartyOption, False)


def update_credOccur():
    '''Call this after events.update_config'''
    global credOccur, E1_entrance_schedule, E2_entrance_schedule, E1_thirdPartyOption, E2_thirdPartyOption
    f = open(path+'/json/credOccur.json')
    credOccur = json.load(f)
    f.close()
    if "Entrances" in credOccur:
        for entrance in credOccur["Entrances"]:
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
    # # print("here",config.get("EntranceName",{}).get("E1",None) == entrance_id)
    if entrance_id and entrance_id == config.get("EntranceName", {}).get("E1", None):
        # # print("here")
        open_door("E1")
    elif entrance_id and entrance_id == config.get("EntranceName", {}).get("E2", None):
        open_door("E2")


def open_GEN_OUT(GEN_OUT_NAME, timer, GenNo):
    relay.open_GEN_OUT(GEN_OUT_NAME, timer, GenNo)

def activate_buzz(entrance, timing):
    '''
    Activates the buzzer at <entrance> for a set amount of time. The request is
    submitted to the thread_pool_executor to be run asychronously.

        Parameters:
            entrance (Any): Entrance ID based on config.json
            time: Duration in seconds for how long to activate the buzzer for
    '''
    # Imports only used in this function
    import eventActionTriggerConstants
    from executor import thread_pool_executor

    # Helper function to send task to thread_pool_executor
    def thread_pool_helper(pin, timing):
        ping_timer = Timer()

        ping_timer.start()
        while not ping_timer.check(timing):
            GPIOconfig.pi.write(pin, 1)
        ping_timer.stop()

        GPIOconfig.pi.write(pin, 0)

    if entrance is eventActionTriggerConstants.BOTH_ENTRANCE:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_IN_Buzz, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_OUT_Buzz, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_IN_Buzz, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_OUT_Buzz, timing)
        return

    if entrance == E1:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_IN_Buzz, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_OUT_Buzz, timing)
    elif entrance == E2:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_IN_Buzz, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_OUT_Buzz, timing)

def activate_led(entrance, timing):
    '''
    Activates the LED at <entrance> for a set amount of time. The request is
    submitted to the thread_pool_executor to be run asychronously.

        Parameters:
            entrance (Any): Entrance ID based on config.json
            time: Duration in seconds for how long to activate the LED for
    '''
    # Imports only used in this function
    import eventActionTriggerConstants
    from executor import thread_pool_executor

    # Helper function to send task to thread_pool_executor
    def thread_pool_helper(pin, timing):
        ping_timer = Timer()

        ping_timer.start()
        while not ping_timer.check(timing):
            GPIOconfig.pi.write(pin, 1)
        ping_timer.stop()
        
        GPIOconfig.pi.write(pin, 0)

    if entrance is eventActionTriggerConstants.BOTH_ENTRANCE:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_IN_Led, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_OUT_Led, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_IN_Led, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_OUT_Led, timing)
        return

    if entrance == E1:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_IN_Led, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E1_OUT_Led, timing)
    elif entrance == E2:
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_IN_Led, timing)
        thread_pool_executor.submit(thread_pool_helper, GPIOconfig.E2_OUT_Led, timing)

def led_and_buzzer_correct_cred(entrance_id):
    '''
    Buzzes and lights up LED to show that the correct credentials were entered,
    when opening the door. Submits the thread_pool_executor to run async.
    Currently only triggers the IN Buzzer and LED, may need to include the OUT
    one as well.

        Parameters:
            entrance_id (Any): Entrance ID based on config.json
    '''
    from executor import thread_pool_executor

    # Buzz for 0.2 seconds, light up LED for 2.2 seconds
    def thread_pool_buzz_led(buzz_pin, led_pin):
        GPIOconfig.pi.write(buzz_pin, 1)
        GPIOconfig.pi.write(led_pin, 1)
        time.sleep(0.2)
        GPIOconfig.pi.write(buzz_pin, 0)
        time.sleep(2)
        GPIOconfig.pi.write(led_pin, 0)
    
    if entrance_id == E1:
        thread_pool_executor.submit(
            thread_pool_buzz_led, GPIOconfig.E1_OUT_Buzz, GPIOconfig.E1_OUT_Led)
        thread_pool_executor.submit(
            thread_pool_buzz_led, GPIOconfig.E1_IN_Buzz, GPIOconfig.E1_IN_Led)
    elif entrance_id == E2:
        thread_pool_executor.submit(
            thread_pool_buzz_led, GPIOconfig.E2_OUT_Buzz, GPIOconfig.E2_OUT_Led)
        thread_pool_executor.submit(
            thread_pool_buzz_led, GPIOconfig.E2_IN_Buzz, GPIOconfig.E2_IN_Led)

def led_and_buzzer_wrong_cred(entrance_id):
    '''
    Buzzes to show that the wrong credentials were entered, when opening the
    door. Submits the thread_pool_executor to run async.
    Currently only triggers the IN Buzzer, may need to include the OUT one as
    well.

        Parameters:
            entrance_id (Any): Entrance ID based on config.json
    '''
    from executor import thread_pool_executor

    # Buzz for 3 times in quick succession
    def thread_pool_buzz(pin):
        for i in range(0,3):
            GPIOconfig.pi.write(pin, 1)
            time.sleep(0.1)
            GPIOconfig.pi.write(pin, 0)
            time.sleep(0.1)
    
    if entrance_id == E1:
        thread_pool_executor.submit(thread_pool_buzz, GPIOconfig.E1_OUT_Buzz)
        thread_pool_executor.submit(thread_pool_buzz, GPIOconfig.E1_IN_Buzz)
    elif entrance_id == E2:
        thread_pool_executor.submit(thread_pool_buzz, GPIOconfig.E2_OUT_Buzz)
        thread_pool_executor.submit(thread_pool_buzz, GPIOconfig.E2_IN_Buzz)

# keep track of wiegand values and pins
# check if person allowed to enter
# trigger relays
# record Trans
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
        # # print(f"recording {auth_method_name} at {entrancename}")
        # eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction,  "", list(access_group.keys())[0])
        
        pinsvalue.clear()
        credentials.clear()
        if timeout_cred.status():
            timeout_cred.stop()

    def open_door():
        '''opens the door, set mags to allow open, update server events'''
        # # print("open")
        # logger.info("Trigger open_door method")
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


    # Process the pin value inputed by user
    def process_pin_value(value):
        # print("value={}".format(value))
        if 0 <= value <= 9:  # normal input
            if len(pinsvalue) > MAX_PIN_LENGTH:
                return False  # Indicate processing should stop
            pinsvalue.append(str(value))
        elif value == 10:  # clear input
            pinsvalue.clear()
        elif value == 11:  # submit
            if pinsvalue:
                credentials[pin_type] = ''.join(pinsvalue)
                pinsvalue.clear()
                return True  # Indicate that credential was added
        return False  # Default case, credential not added

    # credential_added means user input has ended
    # logger.info("bits={} value={}".format(bits, value))
    # print("bits={} value={}".format(bits, value))

    # print(bits, value)
    print("bits before checks={} value before edits={}".format(bits, value)) # TODO: REMOVE
    
    credential_added = False
    if bits == pin_bits:  # 1 number keyed in
        credential_added = process_pin_value(value)

    elif bits == card_bits:  # card
        print("Base value before transformation: ", value) # TODO: REMOVE
        print("Binary value: ", "{:026b}".format(value)) # TODO: REMOVE
        credentials[card_type] = "0" + str(int("{:026b}".format(value)[1:25], 2))
        # logger.info("Card detected: bits={} value={}".format(bits, "0" + str(int("{:026b}".format(value)[1:25], 2))))
        print(str(datetime.now()) + " Card detected: bits={} value={}".format(
            bits, "0" + str(int("{:026b}".format(value)[1:25], 2))))
        credential_added = True

    elif bits == 8:  # if we receive an 8-bit number, split into two 4-bit values, means user press very quickly
        high_digit = (value >> 4) & 0xF  # Extract the high 4 bits
        low_digit = value & 0xF  # Extract the low 4 bits

        # Process each 4-bit value sequentially
        credential_added = process_pin_value(high_digit)
        if not credential_added:  # Only process the second value if the first one doesn't complete the credential
            credential_added = process_pin_value(low_digit)

    elif bits == 12:  # 12-bit, split into three 4-bit values, means user pressed even more quickly
        first_digit = (value >> 8) & 0xF  # Extract the first 4 bits
        second_digit = (value >> 4) & 0xF  # Extract the second 4 bits
        third_digit = value & 0xF  # Extract the third 4 bits
        credential_added = process_pin_value(first_digit)

        if not credential_added:
            credential_added = process_pin_value(second_digit)

        if not credential_added:
            credential_added = process_pin_value(third_digit)

    # checking for creds
    # 1 check master password
    # 2 check auth method (if cred entered not in curr cred schedule, reset)
    # 3 check person creds
    if not credentials:
        return
    
    try:
        device_details = {}
        entrance_details = {}
        credentialLookup = {}

        for entrance_list in credOccur.get("Entrances", []):
            if "Entrance" in entrance_list and entrance_list["Entrance"] == entrancename:
                entrance_details = entrance_list.get("EntranceDetails", {})
                device_details = entrance_details.get("AuthenticationDevices", {}).get(entrance_direction, {})

        if not entrance_details:  # entrance not found, quit
            eventsMod.record_unauth_scans(None, None, entrance_direction)
            led_and_buzzer_wrong_cred(entrancename)
            return
        
        credentialLookup = credOccur.get("CredentialLookup", {})

        # Check master password
        if "Masterpassword" in device_details and credentials.get(pin_type) == device_details["Masterpassword"]:
            eventsMod.record_masterpassword_used("Master Pin", entrancename, entrance_direction)
            led_and_buzzer_correct_cred(entrancename)
            open_door()
            reset_cred_and_stop_timer()
            return

        # Check auth method
        auth_method_name = device_details["defaultAuthMethod"]
        for auth_method in device_details.get("AuthMethod", []):
            if "Method" in auth_method and verify_datetime(auth_method.get("Schedule", {})):
                auth_method_name = auth_method["Method"]
                break

        auth_method_is_and = and_delimiter in auth_method_name
        auth_method_keys = auth_method_name.split(and_delimiter) if auth_method_is_and else auth_method_name.split(or_delimiter)

        print("auth_method_name: ", auth_method_name) # TODO: REMOVE
        print("auth_method_keys: ", auth_method_keys) # TODO: REMOVE
        print("credentials: ", credentials) # TODO: REMOVE

        # Check for credentials not in auth_method_keys
        if any(map(lambda k: k not in auth_method_keys, credentials.keys())):
            eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction)
            led_and_buzzer_wrong_cred(entrancename)
            reset_cred_and_stop_timer()
            return

        # Have some credentials but need more
        if ((auth_method_is_and and any(map(lambda k: k in credentials, auth_method_keys)))
                and not all(map(lambda k: k in credentials, auth_method_keys))):
            print("waiting for more credentials")
            return

        # Check if need to check if cred belongs to someone
        if ((auth_method_is_and and all(map(lambda k: k in credentials, auth_method_keys))) or
           ((not auth_method_is_and) and any(map(lambda k: k in credentials, auth_method_keys)))):
            # Check person cred
            person_ids_checked = set()

            for cred_type, cred_value in credentials.items():
                cred_info = credentialLookup.get(cred_value)
                if cred_info:
                    # print("person found")
                    person_id = cred_info["PersonId"]
                    if person_id not in person_ids_checked:
                        person_ids_checked.add(person_id)
                        access_group_id = cred_info["AccessGroup"]
                        access_group_info = next((ag for ag in entrance_details.get("AccessGroups", []) if ag["GroupId"] == access_group_id), None)
                        # print("AG found: ", access_group_info)

                        if access_group_info and verify_datetime(access_group_info.get('Schedule', {})):
                            # print("AG schedule active")
                            led_and_buzzer_correct_cred(entrancename)
                            open_door()
                            if "Pin" == auth_method_name:
                                eventsMod.pin_only_used(entrancename, entrance_direction)
                            else:
                                eventsMod.record_auth_scans(person_id, access_group_id, auth_method_name, entrancename, entrance_direction)
                            reset_cred_and_stop_timer()
                            return

                        if "Pin" == auth_method_name:
                            eventsMod.invalid_pin_used(entrancename, entrance_direction)
                        else:
                            eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction, person_id, access_group_id)
                        led_and_buzzer_wrong_cred(entrancename)
                        reset_cred_and_stop_timer()
                        return

            if "Pin" == auth_method_name:
                eventsMod.invalid_pin_used(entrancename, entrance_direction)
            else:
                eventsMod.record_unauth_scans(auth_method_name, entrancename, entrance_direction)
            led_and_buzzer_wrong_cred(entrancename)
            reset_cred_and_stop_timer()
            return

    except Exception as e:
        print(f"Exception occurred: {e}")

def check_for_masterpassword(credentials, entrancename, entrance_direction, credOccur):
    for entranceslist in credOccur.get("Entrances", []):
        if entranceslist["Entrance"] == entrancename:
            for devicenumber, devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
                if devicedetails["Direction"] == entrance_direction:
                    if credentials[0] == devicedetails["Masterpassword"]:
                        return True
    return False

def verify_authtype(entrance, device, credOccur):
    for entranceslist in credOccur.get("Entrances", []):
        if entranceslist["Entrance"] == entrance:
            for devicenumber, devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
                if devicedetails["Direction"] == device:
                    for methoddict in devicedetails["AuthMethod"]:
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
    ## print(schedule)
    ## print(type(schedule))
    ## print(str(date.today()))
    # print(datetime.now())
    for scheduledate,scheduletime in schedule.items():
        ## print(scheduledate,scheduletime)
        if scheduledate == str(date.today()):
            # print("today in schedule")
            for timing in scheduletime:
                now = datetime.now().time()
                start = datetime.strptime(timing["starttime"], "%H:%M").time()
                if timing["endtime"] != "24:00":
                    end = datetime.strptime(timing["endtime"], "%H:%M").time()
                        
                    if now >= start and now < end:
                        # print("now in schedule") # strictly within
                        return True
                else:
                    if now >= start:
                        # print("now in schedule") # strictly within
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

    # # print(verify_zone_status(entrance,entrancestatus,persondetails))
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
# # print(verify_zone_status("E1R1","In",persondetails))
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

    print(f"{gpio} Mag opened")

    if gpio == E1_Mag:
        timeout_mag_E1.start()
        # print(f"{E1} is opened at " + str(datetime.now()))
        if mag_E1_allowed_to_open:
            eventsMod.record_mag_opened(E1)
        else:
            eventsMod.record_mag_opened_warning(E1)

    if gpio == E2_Mag:
        timeout_mag_E2.start()
        # print(f"{E2} is opened at " + str(datetime.now()))
        if mag_E2_allowed_to_open:
            eventsMod.record_mag_opened(E2)
        else:
            eventsMod.record_mag_opened_warning(E2)

    mag_detects_rising.last_call_time = time.time()

mag_detects_rising.last_call_time = 0

def mag_detects_falling(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    print(f"{gpio} Mag closed")

    if time.time() - mag_detects_falling.last_call_time < debounce_delay:
        return

    if gpio == E1_Mag:
        timeout_mag_E1.stop()
        # print(f"{E1} is closed at " + str(datetime.now()))
        mag_E1_allowed_to_open = False
        eventsMod.record_mag_closed(E1)

    if gpio == E2_Mag:
        timeout_mag_E2.stop()
        # print(f"{E2} is closed at " + str(datetime.now()))
        mag_E2_allowed_to_open = False
        eventsMod.record_mag_closed(E2)

    mag_detects_falling.last_call_time = time.time()

mag_detects_falling.last_call_time = 0


def button_detects_change(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    # debounce logic
    if time.time() - button_detects_change.last_call_time < debounce_delay:
        return

    # print(gpio, "gpio")

    # handle button reader
    if gpio == E1_Button:
        # logger.info(f"{E1} push button1 is pressed at " + str(datetime.now()))
        mag_E1_allowed_to_open = True
        relay.trigger_relay_one(E1_thirdPartyOption)
        eventsMod.record_button_pressed(E1, "Security Guard Button")

    elif gpio == E2_Button:
        # logger.info(f"{E2} push button2 is pressed at " + str(datetime.now()))
        mag_E2_allowed_to_open = True
        relay.trigger_relay_two(E2_thirdPartyOption)
        eventsMod.record_button_pressed(E2, "Security Guard Button")

    # update last call time
    button_detects_change.last_call_time = time.time()

# initialize the last call time
button_detects_change.last_call_time = 0
