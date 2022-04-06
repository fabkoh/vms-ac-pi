
from datetime import datetime, date
from updateserver import update_external_zone_status
import relay
import eventsMod
import json 
import time
import updateserver


'''
    1. contains class Timer 
    2. check_for_wiegand
    3. bits_reader
'''

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
    
    def check(self,TIME):
        """return True if current_elapsed_time exceeds TIME"""
        current_elapsed_time = time.perf_counter() - self._start_time
        if current_elapsed_time > TIME:
            return True
        
        return False

    def status(self):
        """return True if timing has started"""
        if self._start_time:
            return True 
        return False

filerules = open('json/credOccur.json') 
credOccur = json.load(filerules)

fileconfig = open('json/config.json')
config = json.load(fileconfig)
GPIOpins = config["GPIOpins"]
TIMEOUT = config["TIMEOUT"]

E1 = config["EntranceName"]["E1"]
E2 = config["EntranceName"]["E2"]

E1_Mag= int(GPIOpins["E1_Mag"])
E1_Button= int(GPIOpins["E1_Button"])

E2_Mag= int(GPIOpins["E2_Mag"])
E2_Button= int(GPIOpins["E2_Button"])

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

DEFAULT_CRED_TIMEOUT = 20
DEFAULT_MAG_TIMEOUT = 10
DEFAULT_BUZZER_TIMEOUT = 10

MAX_PIN_LENGTH = 6

try:
    CRED_TIMEOUT_E1 = int(TIMEOUT["CRED_TIMEOUT_E1"])  #number of seconds to wait before credentials arrays is cleared automaically 
except:
    CRED_TIMEOUT_E1 = DEFAULT_CRED_TIMEOUT
try:
    CRED_TIMEOUT_E2 = int(TIMEOUT["CRED_TIMEOUT_E2"])  #number of seconds to wait before credentials arrays is cleared automaically 
except:
    CRED_TIMEOUT_E2 = DEFAULT_CRED_TIMEOUT
try:
    MAG_TIMEOUT_E1 = int(TIMEOUT["MAG_TIMEOUT_E1"])  #number of seconds to wait before credentials arrays is cleared automaically 
except:
    MAG_TIMEOUT_E1 = DEFAULT_MAG_TIMEOUT
try:
    MAG_TIMEOUT_E2 = int(TIMEOUT["MAG_TIMEOUT_E2"])  #number of seconds to wait before credentials arrays is cleared automaically 
except:
    MAG_TIMEOUT_E2 = DEFAULT_MAG_TIMEOUT
try:
    BUZZER_TIMEOUT_E1 = int(TIMEOUT["BUZZER_TIMEOUT_E1"])  #number of seconds to wait before buzzer is triggered automaically 
except:
    BUZZER_TIMEOUT_E1 = DEFAULT_BUZZER_TIMEOUT
try:
    BUZZER_TIMEOUT_E2 = int(TIMEOUT["BUZZER_TIMEOUT_E2"])
except:
    BUZZER_TIMEOUT_E2 = DEFAULT_BUZZER_TIMEOUT

credentials_E1_IN = [] #array to store credentials
credentials_E1_OUT = [] #array to store credentials
credentials_E2_IN = [] #array to store credentials
credentials_E2_OUT = [] #array to store credentials

pinsvalue_E1_IN = []  #array to store pins
pinsvalue_E1_OUT = []  #array to store pins
pinsvalue_E2_IN = []  #array to store pins
pinsvalue_E2_OUT = []  #array to store pins


#takes in string wiegand value, return name, passwords, accessgroup and schedule 
def check_for_wiegand(value):
    for entranceslist in credOccur:
        Accessgroups = entranceslist["EntranceDetails"]["AccessGroups"]
        for specificAccessGroup in Accessgroups:
            for groupName, groupdetails in specificAccessGroup.items():
                for persondetails in groupdetails["Persons"]:

                    diffpassword = list()
                    authmethod = None

                    # check wiegand value belongs to which person, add the rest of wiegand values and pins to diffpassowrd 
                    for type,password in persondetails["Credentials"].items():
                        if value == password:
                            authmethod = type
                            personName = persondetails["Name"]
                
                        if type != authmethod:
                            diffpassword.append(password)
                    
                    # once done, return the data
                    if authmethod:
                        return {"Name": personName,"diffpassword" : diffpassword, "AccessGroup": groupName,"Schedule":groupdetails["Schedule"]}


# keep track of wiegand values and pins 
# check if person allowed to enter 
# trigger relays 
# record Trans
def reader_detects_bits(bits, value,entrance):
    print("bits={} value={}".format(bits, value))
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open


    entrancename = config["EntranceName"][entrance.split("_")[0]]
    entrance_direction = entrance.split("_")[1]

    if entrance == "E1_IN":
        credentials = credentials_E1_IN
        pinsvalue = pinsvalue_E1_IN
        timeout_cred = timeout_cred_E1_IN

    if entrance == "E1_OUT":
        credentials = credentials_E1_OUT
        pinsvalue = pinsvalue_E1_OUT
        timeout_cred = timeout_cred_E1_OUT

    if entrance == "E2_IN":
        credentials = credentials_E2_IN
        pinsvalue = pinsvalue_E2_IN
        timeout_cred = timeout_cred_E2_IN

    if entrance == "E2_OUT":
        credentials = credentials_E2_OUT
        pinsvalue = pinsvalue_E2_OUT
        timeout_cred = timeout_cred_E2_OUT


    # if reader_currently_used != "" and reader_currently_used != entrance_direction:
    #     return

    # reader_currently_used = entrance_direction
    if bits == 4:
        if not timeout_cred.status():
            timeout_cred.start()
        if len(pinsvalue) <= MAX_PIN_LENGTH: #unable to type pin before detecting wiegand values
            pincollector(credentials,pinsvalue,value,timeout_cred)
        else:
            del pinsvalue[:]

    if bits == 26:
        credcollector(credentials,str(value),timeout_cred)

        # name, passwords, accessgroup and schedule
    try:
        persondetails = check_for_wiegand(credentials[0])
    except:
        persondetails = {}




    authtype = verify_authtype(entrancename,entrance_direction)
    print(entrancename, entrance_direction, authtype)
    try:
        authlength = len(authtype.split(","))
    except:
        authlength = 1
    
    if len(credentials) == 1:
        if check_for_masterpassword(credentials,entrancename,entrance_direction):
            print("Authenticated")
            if entrance.split("_")[0] == "E1":
                mag_E1_allowed_to_open = True
                relay.trigger_relay_one()
            if entrance.split("_")[0] == "E2":
                mag_E2_allowed_to_open = True
                relay.trigger_relay_two()
            
            timeout_cred.stop()
            del pinsvalue[:]
            del credentials[:]       
            eventsMod.record_masterpassword_used(authtype,entrancename,entrance_direction)
            updateserver.update_server_events()
        
    '''
    if value == 36443438 or value == 36443419:
        print("Authenticated")
        relay.trigger_relay_one()
        update_zone_status(entrance,entrance_direction,persondetails)
        eventsMod.record_auth_scans(persondetails,authtype,entrancename,entrance_direction)
    '''
    if authlength == len(credentials):
        timeout_cred.stop()
        if verify_credentials(authlength,credentials,persondetails):
            if verify_antipassback(entrancename):
                if verify_zone_status(entrance,entrance_direction,persondetails):
                    print("Authenticated")
                    if entrance.split("_")[0] == "E1":
                        mag_E1_allowed_to_open = True
                        relay.trigger_relay_one()
                    if entrance.split("_")[0] == "E2":
                        mag_E2_allowed_to_open = True
                        relay.trigger_relay_two()
                    
                    update_zone_status(entrance,entrance_direction,persondetails)
                    eventsMod.record_auth_scans(persondetails,authtype,entrancename,entrance_direction)
                    updateserver.update_server_events()
                else:
                    print("Denied, antipassback")
                    eventsMod.record_antipassback(authtype,entrancename,entrance_direction)
                    updateserver.update_server_events()
            else:
                print("Authenticated")
                if entrance.split("_")[0] == "E1":
                    mag_E1_allowed_to_open = True
                    relay.trigger_relay_one()
                if entrance.split("_")[0] == "E2":
                    mag_E2_allowed_to_open = True
                    relay.trigger_relay_two()
                eventsMod.record_auth_scans(persondetails,authtype,entrancename,entrance_direction)
                updateserver.update_server_events()
        else:
            print("Denied")
            eventsMod.record_unauth_scans(authtype,entrancename,entrance_direction)
            updateserver.update_server_events()


def check_for_masterpassword(credentials,entrancename,entrance_direction):
    for entranceslist in credOccur:
        if entranceslist["Entrance"] == entrancename:
            for devicenumber,devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
                if devicedetails["Direction"] == entrance_direction:
                    if credentials[0] == devicedetails["Masterpassword"]:
                        return True
    return False

#take in verifydetails("MainDoor","In") return auth type
def verify_authtype(entrance,device):
    #for data in list of entrances
    for entranceslist in credOccur:
        if entranceslist["Entrance"] == entrance:
            for devicenumber,devicedetails in entranceslist["EntranceDetails"]["AuthenticationDevices"].items():
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

def verify_datetime(schedule):
    #print(schedule)
    #print(type(schedule))

    for scheduledate,scheduletime in schedule.items():
        #print(scheduledate,scheduletime)
        if scheduledate == str(date.today()):
            for timing in scheduletime:
                now_hour = datetime.now().strftime(("%H"))
                now_min = datetime.now().strftime(("%M"))
                start = timing["starttime"]
                end = timing["endtime"]
                start_hour = start.split(":")[0]
                start_min = start.split(":")[1]
                end_hour = end.split(":")[0]
                end_min = end.split(":")[1]

                
                if now_hour > start_hour and now_hour < end_hour: # strictly within
                    return True
                
                if now_hour == start_hour:
                    if now_min >= start_min:
                        return True
                
                if now_hour == end_hour:
                    if end_min > now_min:
                        return True

    return False 


# takes in wiegand value in strings and add to credentials list 
def credcollector(credentials,cred,timeout_cred):
    credentials.append(cred)
    # if it is the first wiegand value, start timing 
    if len(credentials) == 1:
        #if timing has started, stop and restart
        if timeout_cred.status(): 
            timeout_cred.stop()
        timeout_cred.start()
        print("started")

    print(credentials)

# takes in pin values and add to pinsvalue list 
def pincollector(credentials,pinsvalue,pin,timeout_cred):
    
    if pin >= 0 and pin <= 9:
        pinsvalue.append(str(pin))
    elif pin == 10: #               * means CLEAR pinvalue list
        del pinsvalue [:]
        
    elif pin == 11: #               # means ADD pinvalue string to credentials and CLEAR list
        credcollector(credentials,"".join(pinsvalue),timeout_cred)
        del pinsvalue [:]    

    print(pinsvalue)


# return True if person is allowed to enter 
# check if all wiegand values and pins are correct 
#check if person's Accessgroup is allowed to enter 
def verify_credentials(num,credentials,persondetails):

    if len(credentials) == 1 and num == 1 :

        if persondetails and verify_datetime(persondetails["Schedule"]): 
            del credentials [:]
            return True
        else:
            del credentials [:]
            return False
    
    elif len(credentials) == 2 and num == 2:
        try:
            if credentials[1] in persondetails["diffpassword"] and verify_datetime(persondetails["Schedule"]):
                del credentials [:]
                return True
            else:
                del credentials [:]
                return False
        except:
            del credentials [:]
            return False

    return False

#check if person has entered the zone
# entrance = e.g. "E1R1"
#- if In
# 	- if person inside local jsons, not allowed to enter
# 	- if person not inside local jsons, allowed to enter, add to json
# - if out 
# 	- if person inside local json, allowed to leave and remove from json
# 	- if person not inside local json, not allowed to leave 

def verify_zone_status(entrance,entrancestatus,persondetails):
    filename = "json/"+  "status.json"
    with open(filename,"r") as checkfile:
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata ={entrance[:2]:[]}

        if entrancestatus == "IN": #check if person inside 
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

def update_zone_status(entrance,entrancestatus,persondetails):

    filename = "json/"+"status.json"
    with open(filename,"r") as checkfile:
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata ={"controllerId": "","E1":[],"E2":[]}
    
    #print(verify_zone_status(entrance,entrancestatus,persondetails))
    if verify_zone_status(entrance,entrancestatus,persondetails):
        controllerId = config["controllerConfig"][0]["controllerId"]
        dictionary = {"Name":persondetails["Name"],"AccessGroup": persondetails["AccessGroup"]}
        with open(filename,"w+") as outfile:
            updateserver.update_external_zone_status(controllerId, entrance[:2],dictionary,entrancestatus)  

            if entrancestatus == "In":   
                checkdata[entrance[:2]].append(dictionary)
                json.dump(checkdata,outfile,indent=4) 
                
            elif entrancestatus == "Out" :
                for person in checkdata[entrance[:2]]:
                    if persondetails['Name'] == person["Name"] and persondetails["AccessGroup"] == person["AccessGroup"]:
                        checkdata[entrance[:2]].remove(person)       
                json.dump(checkdata,outfile,indent=4) 



# persondetails = {"Name": "Bryan","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}
# print(verify_zone_status("E1R1","In",persondetails))
# update_zone_status("E1R1","In",persondetails)

#check if antipassback if required 
def verify_antipassback(entrancename):
    #read from credOccur.json
    for entrancelist in credOccur:
        if entrancelist["Entrance"] == entrancename:
            if entrancelist["EntranceDetails"]["Antipassback"] == "Yes":
                return True 
    
    return False 


def mag_detects_rising(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    if gpio == E1_Mag:
        timeout_mag_E1.start()
        print(f"{E1} is opened at " + str(datetime.now()))
        if mag_E1_allowed_to_open:
            eventsMod.record_mag_changes(E1,"opened")
        else:
            eventsMod.record_mag_changes(E1,"WARNING : opened without authentication")
        updateserver.update_server_events()

    if gpio == E2_Mag:
        timeout_mag_E2.start()
        print(f"{E2} is opened at " + str(datetime.now()))
        if mag_E2_allowed_to_open:
            eventsMod.record_mag_changes(E2,"opened")
        else:
            eventsMod.record_mag_changes(E2,"WARNING : opened without authentication")
        updateserver.update_server_events()

    
def mag_detects_falling(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    if gpio == E1_Mag:
        timeout_mag_E1.stop()
        print(f"{E1} is closed at " + str(datetime.now()))
        mag_E1_allowed_to_open = False
        eventsMod.record_mag_changes(E1,"closed")
        updateserver.update_server_events()

    if gpio == E2_Mag:
        timeout_mag_E2.stop()
        print(f"{E2} is closed at " + str(datetime.now()))
        mag_E2_allowed_to_open = False
        eventsMod.record_mag_changes(E2,"closed")
        updateserver.update_server_events()


def button_detects_change(gpio, level, tick):
    global mag_E1_allowed_to_open
    global mag_E2_allowed_to_open

    if gpio == E1_Button:
        print(f"{E1} push button is pressed at " + str(datetime.now()))
        mag_E1_allowed_to_open = True
        relay.trigger_relay_one()
        eventsMod.record_button_pressed(E1,"Security Guard Button")
        updateserver.update_server_events()

    if gpio == E2_Button:
        print(f"{E2} push button is pressed at " + str(datetime.now()))
        mag_E2_allowed_to_open = True
        relay.trigger_relay_two()
        eventsMod.record_button_pressed(E2,"Security Guard Button")
        updateserver.update_server_events()



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

