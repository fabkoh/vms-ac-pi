import json
import time

file = open("json/eventActionTriggers.json")
data = json.load(file)

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

def GEN_OUT_4_function():
    print("GEN_OUT_4")

def GEN_OUT_3_function():
    print("GEN_OUT_3")

def GEN_OUT_2_function():
    print("GEN_OUT_2")

def GEN_OUT_1_function():
    print("GEN_OUT_2")

def sendEmail_function():
    print("sendEmail")

def sendSMS_function():
    print("sendSMS")

#controllerId in string
# eventaction in list
def external_controller_GEN_OUT_function(controllerId,eventaction):
    print(controllerId,type(controllerId))
    print(eventaction,type(eventaction))

def external_alarm_function():
    pass

#relay alr written 

def notification_function():
    pass

timeout_buzzer = Timer()

# for eventActionTriggers in data:
#     trigger = []
#     action = []
#     for dictkey, dictvalue in eventActionTriggers.items():

#         if dictkey == "EventTrigger":
#             for eventrigger in dictvalue:
#                 trigger.append(eventrigger)
#         if dictkey == "EventAction":
#             for eventaction in dictvalue:
#                 action = eventaction
#     #print(trigger,action)
#     exec(f"if {trigger[0]} and {trigger[1]} and {trigger[2]}: {action}_function()")


# takes in eventtrigger and calls event actions 
def check_for_EventTrigger_and_EventAction(EventTrigger):
    for eventActionTriggers in data:
        trigger = []
        action = []
        external = []
        for dictkey, dictvalue in eventActionTriggers.items():

            if dictkey == "EventTrigger":
                for eventrigger in dictvalue:
                    trigger.append(eventrigger)
            if dictkey == "EventAction":
                for eventaction in dictvalue:
                    action.append(eventaction)
            if dictkey == "ExternalControllerAction":
                for externalactions in dictvalue:
                    external.append(externalactions)
        
        #print(trigger,action)
        

        if len(trigger) == 1 and trigger[0] == EventTrigger:

            command_to_execute = ""
            for i in action:
                command_to_execute += f"{i}_function() \n"  
            
            if len(external)>0:
                for controlleraction in external:
                    command_to_execute += f"external_controller_GEN_OUT_function{controlleraction['controllerId'],controlleraction['EventAction']}\n"  
            
            exec(command_to_execute)
            print(command_to_execute)

        elif trigger[-1] == EventTrigger:
            command_to_check_and_execute = ""
            for j in range(len(trigger)):
                #print(trigger[j])
                #has timer 
                if type(trigger[j]) == list and len(trigger[j])>1:
                    # print(trigger[j],type(trigger[j]))
                    if command_to_check_and_execute == "":
                        command_to_check_and_execute += f"if {trigger[j][0]}.check({trigger[j][1]}) "
                    else:
                        command_to_check_and_execute += f"and {trigger[j][0]}.check({trigger[j][1]}) "
            
                # no timer
                # last trigger def no timer cos will only be executed when the event is triggered 
                else:
                    pass
                    
            command_to_execute = ""
            for i in action:
                command_to_execute += f"    {i}_function() \n"  

            if len(external)>0:
                for controlleraction in external:
                    command_to_execute += f"    external_controller_GEN_OUT_function{controlleraction['controllerId'],controlleraction['EventAction']}\n"  
            
            if command_to_check_and_execute != "":
                command_to_check_and_execute += f": \n{command_to_execute}"
            exec(command_to_check_and_execute)
                                        
                # check for previous events with timer

timeout_buzzer.start()
time.sleep(1)
test1 = "GEN_IN_1"
test2 = "GEN_IN_2"
check_for_EventTrigger_and_EventAction(test1)
check_for_EventTrigger_and_EventAction(test2)

# need to write all possible output 
# write dynamic input functions to check if true or false
# single action trigger, unless include timer 
# multiple actions can be triggered 
# need to reset everything back to False


# all events will be sent to eventslog
# SCHEDULE 
# multiple unauth scans within a period of time ( use a script to monitor event logs )


''' 
POSSIBLE EVENTTRIGGER

( WITHOUT TIMER ) SINGLE
----------------------------------------------
Authenticated credential scan 

Un-authenticated credential scan 

Exit push button pressed

Door (magnetic contact) closed 

Door (magnetic contact) opened without authentication 

Door (magnetic contact) opened with authentication 

Door (magnetic contact) remains closed after authenticated cred scan  ??????????????????????????? push button ?

External alarm (coming into our in/out alarm pin) 

General input pins 

General output pins ?????????????????????????????????????

( TIMER ) ALLOW FOR MULTIPLE
----------------------------------------------
Magnetic contact opened 

Reader buzzer & LED ( buzz stop buzz stop / LED flash ) ????????????????????

'''




'''
POSSIBLE EVENTACTION
-----------------------------------------------------------------
External alarm (coming into our in/out alarm pin) 

General output pins (both local and on another controller node) ???????????????????????

Relay pin

Notifications (see notification service)

'''

