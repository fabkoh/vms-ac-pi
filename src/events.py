from datetime import datetime, date
from api import update_external_zone_status
#import relay
import transactionsMod
import json 
import time
import threading
import api


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
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
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



timeout_cred = Timer()  
timeout_mag = Timer()

CRED_TIMEOUT = 10  #number of seconds to wait before credentials arrays is cleared automaically 
MAG_TIMEOUT = 10  #number of seconds to wait before buzzer is triggered automaically 
credentials = [] #array to store credentials
pinsvalue = []  #array to store pins


filerules = open('json/credOccur.json') 
credOccur = json.load(filerules)

fileconfig = open('json/config.json')
config = json.load(fileconfig)



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
def bits_reader(bits, value,entrance):
    print("bits={} value={}".format(bits, value))

    if bits == 4:
        if len(credentials) > 0: #unable to type pin before detecting wiegand values
            pincollector(value) 


    if bits == 26:
        credcollector(str(value))

        # name, passwords, accessgroup and schedule 
        persondetails = check_for_wiegand(credentials[0])

        entrancename = config["EntranceName"][entrance][0]
        entrancestatus = config["EntranceName"][entrance][1]

        authtype = verify_authtype(entrancename,entrancestatus)
        authlength = len(authtype.split(","))

        if verify_credentials(authlength,credentials,persondetails) :
            if verify_antipassback(entrancename):
                if verify_zone_status(entrance,entrancestatus,persondetails):
                    print("Authenticated")
                    #relay.trigger_relay_one()
                    update_zone_status(entrance,entrancestatus,persondetails)
                    transactionsMod.record_auth(persondetails,authtype,entrancename,entrancestatus)
            else:
                print("Authenticated")
                #relay.trigger_relay_one()
                transactionsMod.record_auth(persondetails,authtype,entrancename,entrancestatus)



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
            now_hour = datetime.now().strftime(("%H"))
            now_min = datetime.now().strftime(("%M"))
            start = scheduletime["starttime"]
            end = scheduletime["endtime"]
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
def credcollector(cred):
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
def pincollector(pin):
    if pin >= 0 and pin <= 9:
        pinsvalue.append(str(pin))
    elif pin == 10: #               * means CLEAR pinvalue list
        del pinsvalue [:]
        
    elif pin == 11: #               # means ADD pinvalue string to credentials and CLEAR list
        credcollector("".join(pinsvalue))
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
        if credentials[1] in persondetails["diffpassword"] and verify_datetime(persondetails["Schedule"]):
            del credentials [:]
            return True
        else:
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

        if entrancestatus == "In": #check if person inside 
            try:
                
                for person in checkdata[entrance[:2]]:
                    name = person["Name"]
                    accessgroup = person["AccessGroup"]
                    if persondetails['Name'] == name and persondetails["AccessGroup"] == accessgroup:
                        return False 
            except:
                pass
            return True
        
        elif entrancestatus == "Out":
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
            api.update_external_zone_status(controllerId, entrance[:2],dictionary,entrancestatus)  

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


def cbmagrise(gpio, level, tick):
    print("Entrance 1 is opened at " + str(datetime.now()))
    timeout_mag.start()

    
def cbmagfall(gpio, level, tick):
    print("Entrance 1 is closed at " + str(datetime.now()))
    mag_status_open = False
    timeout_mag.stop()

def cbbutton(gpio, level, tick):
    print("Pb 1 was pushed at " + str(datetime.now()))
    relay.trigger_relay_one()

def check():
    while True:
        if timeout_cred.status(): 
            if timeout_cred.check(CRED_TIMEOUT):
                timeout_cred.stop()
                del credentials [:]

        if timeout_mag.status():
            if timeout_mag.check(MAG_TIMEOUT):
                print("BUZZZZZZZZZZZZZZZZZZ")

        time.sleep(0.1)

# 1st person going in
# bits_reader(26,"s1e97ncksiu","E1R1")
# bits_reader(26,"696955874","E1R1")

# 2nd person going in
# bits_reader(26,"2535645","E1R1")
# bits_reader(26,"ege56g4er","E1R1")

# 2nd person going in AGAIN 
# bits_reader(26,"2535645","E1R1")
# bits_reader(26,"ege56g4er","E1R1")

# 1st person going out
bits_reader(26,"s1e97ncksiu","E1R2")
bits_reader(26,"696955874","E1R2")