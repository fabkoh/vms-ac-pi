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


# how to factor in timing ?
# need to write all possible functions 
# need to reset everything back to False
# max number of event triggers and event action 
# huge while loop running 



