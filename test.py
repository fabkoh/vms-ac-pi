#import pigpio
from datetime import datetime, date
#import relay
#import transactionsMod
import json 
import time
import threading

test = open('test.json')
data = json.load(test)


CRED_TIMEOUT = 10
credentials = []
pinsvalue = []





Accessgroups = data["EntranceDetails"]["AccessGroups"]

#takes in string value, return name, passwords and accessgroup

def check_for_wiegand(value):
    for specificAccessGroup in Accessgroups:
        for groupName, groupdetails in specificAccessGroup.items():
            for persondetails in groupdetails["Persons"]:
                diffpassword = list()
                authmethod = None
                for type,password in persondetails["Credentials"].items():
                    if value == password:
                        authmethod = type
                        personName = persondetails["Name"]
            
                    if type != authmethod:
                        diffpassword.append(password)
                    
                if authmethod:
                    return {"Name": personName,"diffpassword" : diffpassword, "AccessGroup": groupName}



#takes in value (strings) if 4 bits, 

def credcollector(cred):
    credentials.append(cred)
    if len(credentials) == 1:
        if timeout_cred.status(): 
            timeout_cred.stop()
        timeout_cred.start()
        print("started")

    print(credentials)

def pincollector(pin):
    if pin >= 0 and pin <= 9:
        pinsvalue.append(str(pin))
    elif pin == 10: #CLEAR
        del pinsvalue [:]
        
    elif pin == 11: #"ENTER"
        credcollector("".join(pinsvalue))
        del pinsvalue [:]        
    print(pinsvalue)

def verify_credentials(num,credentials,persondetails):
            if len(credentials) == 1 and num == 1 :
                if persondetails:
                    print(persondetails)
                    #opendoor
                else:
                    print("NOT FOUND")
                del credentials [:]
            
            elif len(credentials) == 2 and num == 2:
                if credentials[1] in persondetails["diffpassword"]:
                    #opendoor
                    print(persondetails)
                else:
                    print("NOT FOUND")
                del credentials [:]
            


def callback_e1(bits, value):
    print("bits={} value={}".format(bits, value))

    if bits == 4:
        if len(credentials) > 0:
            pincollector(value)

    if bits == 26:
        credcollector(str(value))

        persondetails = check_for_wiegand(credentials[0])
        authtype = verify_authtype("MainDoor","In")

        verify_credentials(0,credentials,persondetails)


        if authtype == "Card" or authtype == "Fingerprint":
            verify_credentials(1,credentials,persondetails)
            
        
        if authtype == "Card,Pin" or authtype == "Fingerprint,Pin" or "Fingerprint,Card":      
            verify_credentials(2,credentials,persondetails)
            

        if value == 36443419 or value == 36443438:
            print("Authenticated")
            relay.trigger_relay_one()
            print("jere")
            #transactionsMod.record(value,reader,exit)


#take in verifydetails("MainDoor","In") return auth type
def verify_authtype(entrance,device):
    #for data in listofentrances
    if data["Entrance"] == entrance:
        for devicenumber,devicedetails in data["EntranceDetails"]["AuthenticationDevices"].items():
            if devicedetails["Direction"] == device:
                for methoddict in devicedetails["AuthMethod"]:
                    for scheduledate,scheduletime in methoddict["Schedule"].items():
                        if verify_datetime(scheduledate,scheduletime):
                            return methoddict["Method"]

def verify_datetime(scheduledate,scheduletime):
    if scheduledate == str(date.today()):
        now_hour = datetime.now().strftime(("%H"))
        now_min = datetime.now().strftime(("%M"))
        # now_hour = "18"
        # now_min = "00"
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


print(verify_datetime("2022-03-14",{"starttime":"09:00","endtime":"23:00"}))


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
        current_elapsed_time = time.perf_counter() - self._start_time
        if current_elapsed_time > TIME:
            return True
        
        return False

    def status(self):
        if self._start_time:
            return True 
        return False


def inputnum():
    while True:
        value = str(input("Enter value: "))
        bits = int(input("Enter bits: "))
        callback_e1(bits,value)

def check():
    while True:
        if timeout_cred.status(): 
            if timeout_cred.check(CRED_TIMEOUT):
                timeout_cred.stop()
                del credentials [:]
        time.sleep(0.1)

timeout_cred = Timer()

t1=threading.Thread(target=inputnum,)
t2=threading.Thread(target=check,)

t1.start()
t2.start()

