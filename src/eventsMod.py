import json
from datetime import datetime
import os
from updateserver import update_server_events
path = os.path.dirname(os.path.abspath(__file__))

'''
    1. record_auth and record_button to record transLogs in archivedTrans.json and pendingTrans.json
'''

fileconfig = open(path +'/json/config.json')
config = json.load(fileconfig)
controllerSerial = config["controllerConfig"]["controllerSerialNo"]

try:
    MAX_JSON_LENGTH = int(config["archivedMAXlength"]) # max length before first half of jsons get deleted 
except:
    MAX_JSON_LENGTH = 10


'''
persondetails = {   "Name": personName,
                    "diffpassword" : [cardwiegandvalue,fingerwiegandvalue,pin], #everything besides the initial wiegand value used to identify personName  
                    "AccessGroup": AccessgroupName,
                    "Schedule": {
                                "2022-03-14":{"starttime":"18:00","endtime":"23:00"},
                                "2022-03-15": {"starttime":"18:00","endtime":"23:00"}
                                }
                }
authtype = e.g. card    Fingerprint,Pin

entrance =  e.g. MainDoor
status = e.g. In


dictionary 

direction  STRING
eventTime  DATETIME
person     PERSONID
entrance   ENTRANCEID
accessGroup   ACCESSGROUPID
eventActionType   EVENTACTIONTYPEID
controller         CONTROLLERID


'''

#updates pendingLogs.json and send to backend 
#updates archivedLogs.json for backup 
def record_auth_scans(name, accessGroup,authtype,entrance,status):
    dictionary = {
                    "person":{"personId":name},
                    "accessGroup":{"accessGroupId":accessGroup}, 
                    "direction": status,
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 1, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }
    
    update("json/archivedLogs.json",dictionary)
    update("json/pendingLogs.json",dictionary)

#updates pendingLogs.json and send to backend 
#updates archivedLogs.json for backup 
def record_masterpassword_used(authtype,entrance,status):
    dictionary = {
                    "direction": status,
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 2, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    
    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)
    
    
#updates pendingTrans.json and send to backend 
#updates archivedTrans.json for backup 
def record_unauth_scans(authtype,entrance,status, name=None, access_group=None):
    dictionary = {
                    "person":{"personId":name},
                    "accessGroup":{"accessGroupId":access_group}, 
                    "direction": status,
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 2, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    
    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

def record_button_pressed(entrance,name_of_button):

    dictionary = {
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 9, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)
# status = opened/ closed


def record_antipassback(authtype,entrance,status):

    dictionary = {
                    "person":{"personId":name},
                    "accessGroup":{"accessGroupId":accessGroup}, 
                    "direction": status,
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 1, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    dictionary = {
                "direction": status,"entrance":entrance,"eventActionType": "ANTIPASSBACK : authenticated_scan ", 
                "controller":controllerSerial,"eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }
    
    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

def record_mag_opened(entrance):

    dictionary = {
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 4, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

def record_mag_closed(entrance):

    dictionary = {
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 5, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

def record_mag_opened_warning(entrance):

    dictionary = {
                    "entrance": {"entranceId":entrance},
                    "eventActionType": 6, 
                    "controller":{"controllerSerialNo":controllerSerial},
                    "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

# status = started buzzing/ stopped buzzing 
def record_buzzer_start(entrance):

    dictionary = {
                        "entrance": {"entranceId":entrance},
                        "eventActionType": 7, 
                        "controller":{"controllerSerialNo":controllerSerial},
                        "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)

def record_buzzer_end(entrance):

    dictionary = {
                        "entrance": {"entranceId":entrance},
                        "eventActionType": 8, 
                        "controller":{"controllerSerialNo":controllerSerial},
                        "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
        }

    update(path +"/json/archivedLogs.json",dictionary)
    update(path+"/json/pendingLogs.json",dictionary)
    
#update to update json files
def update(file,dictionary):

    #check if current json files exceed max length 
    clear_file_storage(file)

    with open(file,"r+") as outfile:
        try:
            data = json.load(outfile)
        except:
            data = []
        
        data.append(dictionary)
        outfile.seek(0)

        json.dump(data,outfile,indent=4) 
    outfile.close()

    

#delete first half if exceeds length
def clear_file_storage(file):

     with open(file,"r") as checkfile:
        
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata = []

        if len(checkdata) > MAX_JSON_LENGTH:
            checkfile.close()
            with open(file,"w+") as outfile:
                del checkdata[:(int(MAX_JSON_LENGTH/2))]
                json.dump(checkdata,outfile,indent=4) 
        else:
            checkfile.close()



update_server_events()

def main():
    #persondetails = {"Name": "YongNing","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}

    #record_auth_scans(persondetails,"Card","Maindoor","In")
    #record_button_pressed("Maindoor","Security guard button")

    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","Security guard button")
    pass

if __name__ == "__main__":
    main()
