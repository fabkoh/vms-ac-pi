import pigpio
from datetime import datetime, date
import relay
#import transactionsMod
import json 
import time
import threading
import asyncio

test = open('test.json')
data = json.load(test)


CRED_TIMEOUT = 10
MAG_TIMEOUT = 10
credentials = []
pinsvalue = []

E1_R1_D0= 24
E1_R1_D1= 25
E1_R1_Buzz=7
E1_R1_Led=8
E1_R2_D0=22
E1_R2_D1=10
E1_R2_Buzz=11
E1_R2_Led=9
E1_Mag= 6
E1_Button= 5

'''
E2_R1_D0=
E2_R1_D1=
E2_R1_Buzz=
E2_R1_Led=
E2_R2_D0=
E2_R2_D1=
E2_R2_Buzz=
E2_R2_Led=
E2_Mag=
E2_Button=
'''

#initialising pi
pi = pigpio.pi()

#initialising E1_Button for pushbutton1
pi.set_mode(E1_Button, pigpio.INPUT)
#pi.set_pull_up_down(E1_Button, pigpio.PUD_UP)

#E1_Mag for mag contact
pi.set_mode(E1_Mag, pigpio.INPUT) 
pi.set_pull_up_down(E1_Mag, pigpio.PUD_UP)

#E1_R1_Buzz for Buzz
pi.set_mode(E1_R1_Buzz, pigpio.OUTPUT)
pi.write(E1_R1_Buzz, 0)
#pi.write(E1_R1_Buzz, 1)
#pi.set_PWM_dutycycle(E1_R1_Buzz, 255) # PWM full on

#E1_R1_Led for Led
pi.set_mode(E1_R1_Led, pigpio.INPUT) 
pi.write(E1_R1_Led, 0)

#E1_R2_Buzz for Buzz
pi.set_mode(E1_R2_Buzz, pigpio.INPUT) 
pi.write(E1_R2_Buzz, 0)

#E1_R2_Led for Led
pi.set_mode(E1_R2_Led, pigpio.INPUT) 
pi.write(E1_R2_Led, 0)




class decoder:

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):


      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

      self.pi.set_mode(gpio_0, pigpio.INPUT)
      self.pi.set_mode(gpio_1, pigpio.INPUT)

      self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
      self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)
    
      self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
      self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)
      

      
            
            
   def _cb(self, gpio, level,tick):

      """
      Accumulate bits until both gpios 0 and 1 timeout.
      """

      if level < pigpio.TIMEOUT:

         if self.in_code == False:
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0
            self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
            self.pi.set_watchdog(self.gpio_1, self.bit_timeout)
         else:
            self.bits += 1
            self.num = self.num << 1

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # clear gpio 0 timeout
         else:
            self.code_timeout = self.code_timeout & 1 # clear gpio 1 timeout
            self.num = self.num | 1

      else:

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # timeout gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # timeout gpio 1

            if self.code_timeout == 3: # both gpios timed out
               self.pi.set_watchdog(self.gpio_0, 0)
               self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False
               self.callback(self.bits, self.num)
               return

   def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      self.cb_0.cancel()
      self.cb_1.cancel()

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
                    return {"Name": personName,"diffpassword" : diffpassword, "AccessGroup": groupName,"Schedule":groupdetails["Schedule"]}



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
                if persondetails and verify_datetime(persondetails["Schedule"]): 
                    print(persondetails)
                    #opendoor
                else:
                    print("NOT FOUND")
                del credentials [:]
            
            elif len(credentials) == 2 and num == 2:
                try:
                    if credentials[1] in persondetails["diffpassword"] and verify_datetime(persondetails["Schedule"]):
                        #opendoor
                        print(persondetails)
                except:
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
            asyncio.run(relay.trigger_relay_one())
            print("jere")
            #transactionsMod.record(value,reader,exit)


def callback_e2(bits, value):
    print("bits={} value={}".format(bits, value))
    # if value in list of credid
    
    if value == 36443419 or value == 36443438:
        print("Authenticated")
        relay.trigger_relay_two()
        #transactionsMod.record()


#take in verifydetails("MainDoor","In") return auth type
def verify_authtype(entrance,device):
    #for data in listofentrances
    if data["Entrance"] == entrance:
        for devicenumber,devicedetails in data["EntranceDetails"]["AuthenticationDevices"].items():
            if devicedetails["Direction"] == device:
                for methoddict in devicedetails["AuthMethod"]:
                    if verify_datetime(methoddict["Schedule"]):
                            return methoddict["Method"]



                    # for scheduledate,scheduletime in methoddict["Schedule"].items():
                    #     if verify_datetime(scheduledate,scheduletime):
                    #         return methoddict["Method"]


def verify_datetime(schedule):

    for scheduledate,scheduletime in schedule.items():
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



#everytime relay triggers, mag_status_open = True 
# if mag_contact opened but mag_status_open = False, TRIGGER ALARM 

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

def mag():
    cb1 = pi.callback(E1_Mag, pigpio.RISING_EDGE, cbmagrise)
    cb2 = pi.callback(E1_Mag, pigpio.FALLING_EDGE, cbmagfall)
    
    '''
    while True:
        
        if pi.read(6) == 1:
            print("Entrance opened at " + str(datetime.now()))
            
        
        pi.wait_for_edge(6, pigpio.RISING_EDGE)
        print("Entrance 1 is opened at " + str(datetime.now()))
        
        pi.wait_for_edge(6, pigpio.FALLING_EDGE)
        print("Entrance 1 is closed at " + str(datetime.now()))
    ''' 
def buzz():
    pass


def button():
    
    cb3 = pi.callback(E1_Button, pigpio.RISING_EDGE, cbbutton)
    
    '''
    while True: 
        if pi.read(5) == 0:
            print(pi.read(5))
            print("Pb 1 was pushed at " + str(datetime.now()))
            relay.trigger_relay_one()
            print("Here")
    '''

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it".format())

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it".format())

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print("Elapsed time: {} seconds".format(elapsed_time))
    
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
                del pinsvalue [:]

        if timeout_mag.status():
            if timeout_mag.check(MAG_TIMEOUT):
                pi.write(E1_R2_Buzz, 1)
                pi.write(E1_R1_Buzz, 1)
                pi.write(E1_R2_Led, 1)
                pi.write(E1_R1_Led, 1)
        else:
            pi.write(E1_R2_Buzz, 0)
            pi.write(E1_R1_Buzz, 0)
            pi.write(E1_R2_Led, 0)
            pi.write(E1_R1_Led, 0)
                

        time.sleep(0.1)
        
e1r1 = decoder(pi, E1_R1_D0, E1_R1_D1, callback_e1)
e1r2 = decoder(pi, E1_R2_D0, E1_R2_D1, callback_e1)
timeout_cred = Timer()
timeout_mag = Timer()

loop.create_task(while_loop())
loop.create_task(some_func())
loop.run_forever()

# t1 = threading.Thread(target=button)
# t2 = threading.Thread(target=mag)
# t3=threading.Thread(target=check,)

# t1.start()
# t2.start()
# t3.start()