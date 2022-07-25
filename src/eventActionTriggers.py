import datetime
import json
import threading
import time
import os
from eventActionTriggerConstants import *
import relay

path = os.path.dirname(os.path.abspath(__file__))
EVENT_ACTION_TRIGGERS_DATA = []

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

# maps time based (eventTriggerId,entranceId) to time (time.time())
eventTriggerTime={}

# store output events
output_events=[]

def check_datetime(schedule):
    '''Helper function to check if schedule is currently active
    
    Args:
        schedule: schedule adt (cdict mapping date to list of { starttime, endtime }, time is in hh:mm format. Check docs for more info
        
    Returns:
        active: if the schedule is current active
    '''
    time_array = schedule.get(str(datetime.date.today()),None)
    if time_array == None: return False 

    curr_datetime = datetime.datetime.now()
    curr_time = curr_datetime.strftime("%H") + ":" + curr_datetime.strftime("%M") # "HH:MM"
    for timing in time_array:
        start_time = timing.get("starttime","24:00")
        end_time = timing.get("endtime","00:00")
        if start_time <= curr_time <= end_time:
            return True
    return False
    

def flush_output():
    '''Activates output'''
    import events
    import GPIOconfig
    for event in output_events:
        entrance = event.get("entrance",{}).get("entranceId",None)
        if entrance == None:
            if event.get("controller",None) != None:
                entrance=BOTH_ENTRANCE
            else:
                continue # ignore, malformed json

        for output in event.get("outputActions",[]):
            id = output.get("eventActionOutputType",{}).get("eventActionOutputId",None)
            if id == DOOR_OPEN:
                events.open_door_using_entrance_id(entrance)
            elif id == BUZZER:
                print("buzzer")
                GPIOconfig.activate_buzz(entrance,output.get("timerDuration",0))
            elif id == LED:
                print("led")
                GPIOconfig.activate_led(entrance,output.get("timerDuration",0))
            elif id == GEN_OUT_1:
                events.open_GEN_OUT("GEN_OUT_1",output.get("timerDuration",0))
            elif id == GEN_OUT_2:
                events.open_GEN_OUT("GEN_OUT_2",output.get("timerDuration",0))
            elif id == GEN_OUT_3:
                events.open_GEN_OUT("GEN_OUT_3",output.get("timerDuration",0))


    output_events.clear()

def queue_output(event):
    '''Helper function to store output events to activate
    DOES NOT ACTIVATE OUTPUT, CALL flush_output() TO ACTIVATE

    Args: eventManagement object
    '''
    output_events.append(event)

def get_entrance_from_event_management(event_management):
    '''Helper function to return entrance_id from event_management object

    Args:
        event_management (dict): event_management object from eventActionTrigger.json

    Returns:
        entrance_id (int): entrance id
    '''
    entrance = event_management.get("entrance",None)
    if entrance != None:
        return entrance.get("entranceId",None)

    # if its controller, it works for both entrances
    return BOTH_ENTRANCE



def event_trigger_cb(event_trigger):
    print(event_trigger)
    ''' function hook to call everytime an event trigger occurs
    
    Args:
        event_trigger (check eventActionTriggerConstants.py): event_trigger which occurred
    '''
    # if event is timed, activate timer and return, while true loop will handle the rest
    if input_is_timed(event_trigger):
        timer_action = get_timer_event_timer_action(event_trigger)
        event_trigger_type = get_timer_event_event_action_trigger(event_trigger)
        entrance = get_event_entrance(event_trigger)
        if timer_action == START_TIMER:
            eventTriggerTime[(event_trigger_type,entrance)] = time.time()
        elif timer_action == STOP_TIMER:
            eventTriggerTime[(event_trigger_type,entrance)] = None
            # need to reset all events with this event_trigger_type
            # first filter all events with this event_trigger_type
            for event in filter( # filter events with this event_trigger_type
                lambda eventManagement: any(map(
                    lambda inputEvent: inputEvent.get("eventActionInputType",{})
                        .get("eventActionInputId",None) == event_trigger_type,
                    eventManagement.get("inputEvents",[])
                    )) and (entrance is BOTH_ENTRANCE or get_entrance_from_event_management(eventManagement)==entrance), # check if this event management entrance is the same as the event
                EVENT_ACTION_TRIGGERS_DATA
            ):
                activated[event.get("eventManagementId",None)] = False # allow these events to activate again
        return 

    # if event is not timed, check for all events
    # first filter events by if they have event_trigger in them
    event_trigger_id = get_event_trigger_from_event(event_trigger)
    entrance = get_event_entrance(event_trigger)

    for event in filter( # filter events by if they have event_trigger in them
        lambda eventManagement: any(map( # finds if any inputEvent (in events) have event_trigger
            lambda inputEvent: inputEvent.get("eventActionInputType",{})
                .get("eventActionInputId",None) == event_trigger_id,
            eventManagement.get("inputEvents",[])
            )) and check_datetime(eventManagement.get("triggerSchedule",{}))
               and (entrance is BOTH_ENTRANCE or
                    get_entrance_from_event_management(eventManagement) is BOTH_ENTRANCE or
                    get_entrance_from_event_management(eventManagement) == entrance), # check if trigger is currently active
        EVENT_ACTION_TRIGGERS_DATA): 

        event_management_id = event.get("eventsManagementId",None)

        # check if event has been activated before, if so skip this event
        if activated.get(event_management_id,False):
            continue

        valid=True
        entrance=get_entrance_from_event_management(event)
        # check if all time based trigger is valid
        for inputEvent in event.get("inputEvents",[]):
            # each eventManagement has max 1 event based trigger
            # if the event is different, it must be a timer based trigger
            input_event_id = inputEvent.get("eventActionInputType",{}).get("eventActionInputId",None)
            if input_event_id != event_trigger_id: 
                t = eventTriggerTime.get((input_event_id,entrance),None)
                if t == None:
                    t = eventTriggerTime.get((input_event_id,BOTH_ENTRANCE),None)
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
            queue_output(event)
            
    flush_output()
                    
def check_for_only_timer_based_events():
    while True:
        for event in filter( # filter by currently active
            lambda eventManagement: check_datetime(eventManagement.get("triggerSchedule",{})),
            EVENT_ACTION_TRIGGERS_DATA
            ):
            event_management_id = event.get("eventManagementId",None)

            if activated.get(event_management_id,False):
                continue # already activated

            valid=True
            entrance=get_entrance_from_event_management(event)
            for inputEvent in event.get("inputEvents",[]):
                input_id = inputEvent.get("eventActionInputType",{}).get("eventActionInputId",None)
                d = inputEvent.get("timerDuration",None)
                t = eventTriggerTime.get((input_id,entrance),None)
                if t == None:
                    t = eventTriggerTime.get((input_id,BOTH_ENTRANCE),None)
                if (t==None) or (d==None) or (time.time()-t<d): # event is not to be activated
                    valid=False
                    break
            if valid:
                activated[event_management_id] = True # timer based must have activated
                queue_output(event)
                
        flush_output()
        time.sleep(0.1) # throttle

t1 = threading.Thread(target=check_for_only_timer_based_events)
t1.start()

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

External alarm (coming into our in/out alarm pin) 

General input pins 

( TIMER ) ALLOW FOR MULTIPLE
----------------------------------------------
Magnetic contact opened 

Reader buzzer 

LED (buzz stop / LED flash ) 

'''




'''
POSSIBLE EVENTACTION
-----------------------------------------------------------------
External alarm (coming into our in/out alarm pin) 

General output pins (both local and on another controller node) ???????????????????????

Relay pin

Notifications (see notification service) email/ sms

'''

