import json
import threading
import time
import os
from eventActionTriggerConstants import *

path = os.path.dirname(os.path.abspath(__file__))
EVENT_ACTION_TRIGGERS_DATA = None

def update_event_action_triggers():
    global EVENT_ACTION_TRIGGERS_DATA
    f=open(path+"/json/eventActionTriggers.json")
    EVENT_ACTION_TRIGGERS_DATA=json.load(f)
    f.close()

update_event_action_triggers()

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


'''
EVENT ACTION TRIGGERS
Main idea: check through each trigger repeatedy, activate output if trigger conditions are all active

Can be split into 2 parts: finding out if trigger is activated and activating output

FINDING OUT IF TRIGGER IS ACTIVATED
there are 2 kinds of triggers, event based trigger and timer based trigger

time based trigger include "door open for more than 10s"
non timer based triggers include "authenticated scan"

for event management with only timer based triggers, continuously check if all conditions are active to activate output
for event management with a non timer based trigger, check if all timer based triggers are active during the non timer based trigger activation to activate output

and check if the current time is in the trigger schedule

ACTIVATING OUTPUT
check for each output, and call the appropriate functions to activate the output
to prevent multiple activations of triggers with a time based component, have a dict mapping eventManagementId to activation status.
Upon reset of timer based condition, set all eventManagementId with that timer based condition to be able to activate again
'''

# maps eventManagementId to boolean, True means has been activated, False means has not been activated
activated={}

# maps time based eventTriggerId to time (time.time())
eventTriggerTime={}

# store output events
output_events=[]

def flush_output():
    '''Activates output'''
    for output in output_events:
        print(output)
    
    output_events.clear()

def activate_output(output):
    '''Helper function to store output events to activate
    DOES NOT ACTIVATE OUTPUT, CALL flush_output() TO ACTIVATE

    Args: list of output actions
    '''
    output_events.extend(output)

#TODO: implement checking of schedule
def event_trigger_cb(event_trigger):
    ''' function hook to call everytime an event trigger occurs
    
    Args:
        event_trigger (check eventActionTriggerConstants.py): event_trigger which occurred
    '''
    # if event is timed, activate timer and return, while true loop will handle the rest
    if input_is_timed(event_trigger):
        timer_action = get_timer_event_timer_action(event_trigger)
        event_trigger_type = get_timer_event_event_action_trigger(event_trigger)
        if timer_action == START_TIMER:
            eventTriggerTime[event_trigger_type] = time.time()
        elif timer_action == STOP_TIMER:
            eventTriggerTime[event_trigger_type] = None
            # need to reset all events with this event_trigger_type
            # first filter all events with this event_trigger_type
            for event in filter( # filter events with this event_trigger_type
                lambda eventManagement: any(
                    lambda inputEvent: inputEvent.get("eventActionInputType",{})
                        .get("eventActionInputId",None) == event_trigger_type,
                    eventManagement.get("inputEvents",[])
                    ),
                EVENT_ACTION_TRIGGERS_DATA
            ):
                activated[event.get("eventManagementId",None)] = False # allow these events to activate again
        return 

    # if event is not timed, check for all events
    # first filter events by if they have event_trigger in them
    for event in filter( # filter events by if they have event_trigger in them
        lambda eventManagement: any( # finds if any inputEvent (in events) have event_trigger
            lambda inputEvent: inputEvent.get("eventActionInputType",{})
                .get("eventActionInputId",None) == event_trigger,
            eventManagement.get("inputEvents",[])
            ),
        EVENT_ACTION_TRIGGERS_DATA): 

        event_management_id = event.get("eventManagementId",None)

        # check if event has been activated before, if so skip this event
        if activated.get(event_management_id,False):
            continue

        valid=True
        # check if all time based trigger is valid
        for inputEvent in event.get("inputEvents",[]):
            # each eventManagement has max 1 event based trigger
            # if the event is different, it must be a timer based trigger
            if inputEvent.get("inputEventId",None) != event_trigger: 
                t = eventTriggerTime.get(event_management_id,None)
                d = inputEvent.get("timerDuration",None)
                # t is None means trigger has not been active so do not activate
                # time.time()-t is the time elasped, if less than d, the time elapsed is not long enough, so do not activate
                if (t==None) or (d==None) or (time.time()-t<d):
                    valid=False
                    break
        
        if valid:
            # if there are more than 1 inputEvent, there is a timer based trigger
            # thus, need to set this to prevent repeats
            # ex. door opened more than 10s and unauthenticated scan
            # if 2 unauthenicated scans, should only trigger at the first scan
            if len(event.get("inputEvent", [])) > 1:
                activated[event_management_id]=True
            activate_output(event.get("outputActions",[]))
            
    flush_output()
                    
def check_for_only_timer_based_events():
    for event in EVENT_ACTION_TRIGGERS_DATA:
        event_management_id = event.get("eventManagementId",None)
        if activated.get(event_management_id,False):
            continue # already activated
        valid=True
        for inputEvent in event.get("inputEvents",[]):
            d = inputEvent.get("timerDuration",None)
            t = eventTriggerTime.get(event_management_id,None)
            if (t==None) or (d==None) or (time.time()-t<d): # event is not to be activated
                valid=False
                break
        if valid:
            activated[event_management_id] = True # timer based must have activated
            activate_output(event.get("outputActions",[]))
            
    flush_output()
    time.sleep(0.1) # throttle

threading.Thread(target=check_for_only_timer_based_events)

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

