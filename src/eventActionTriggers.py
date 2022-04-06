import json

file = open("json/eventActionTriggers.json")
data = json.load(file)

ALWAYS_TRUE = True
GEN_IN_1 = True
GEN_IN_2 = False
magcontactopened = False
buzzer = False
sendEmail = False
GEN_OUT_3 = False
GEN_OUT_4 = False

def GEN_OUT_4_function():
    print("GEN_OUT_4")

def GEN_OUT_3_function():
    print("GEN_OUT_3")

def sendEmail_function():
    print("sendEmail")

for eventActionTriggers in data:
    trigger = []
    action = []
    for dictkey, dictvalue in eventActionTriggers.items():

        if dictkey == "EventTrigger":
            for eventrigger in dictvalue:
                trigger.append(eventrigger)
        if dictkey == "EventAction":
            for eventaction in dictvalue:
                action = eventaction
    #print(trigger,action)
    exec(f"if {trigger[0]} and {trigger[1]} and {trigger[2]}: {action}_function()")




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

