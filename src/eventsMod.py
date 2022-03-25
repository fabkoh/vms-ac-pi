import json
from datetime import datetime 


'''
    1. record_auth and record_button to record transLogs in archivedTrans.json and pendingTrans.json
'''


MAX_JSON_LENGTH = 10 # max length before first half of jsons get deleted 


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
'''

#updates pendingLogs.json and send to backend 
#updates archivedLogs.json for backup 
def record_auth_scans(persondetails,authtype,entrance,status):
    name = persondetails["Name"]
    accessGroup = persondetails["AccessGroup"]

    dictionary = {"name":name,"accessgroup":accessGroup, "authmethod":authtype,
                "direction": status,"entrance":entrance,"eventActionType": "authenticated_scans", 
                "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }
    
    update("./src/json/archivedLogs.json",dictionary)
    update("./src/json/pendingLogs.json",dictionary)

#updates pendingTrans.json and send to backend 
#updates archivedTrans.json for backup 
def record_button_pressed(entrance,name_of_button):

    dictionary = {"entrance":entrance,"eventActionType": name_of_button+" pressed", 
                "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update("./src/json/archivedLogs.json",dictionary)
    update("./src/json/pendingLogs.json",dictionary)

# status = opened/ closed
def record_mag_changes(entrance,status):

    dictionary = {"entrance":entrance,"eventActionType": status, 
                "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update("./src/json/archivedLogs.json",dictionary)
    update("./src/json/pendingLogs.json",dictionary)

# status = started buzzing/ stopped buzzing 
def record_buzzer(entrance,status):

    dictionary = {"entrance":entrance,"eventActionType":status, 
                "eventTime":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }

    update("./src/json/archivedLogs.json",dictionary)
    update("./src/json/pendingLogs.json",dictionary)
    
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
