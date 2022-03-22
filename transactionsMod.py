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

#updates pendingTrans.json and send to backend 
#updates archivedTrans.json for backup 
def record_auth(persondetails,authtype,entrance,status):
    name = persondetails["Name"]
    accessGroup = persondetails["AccessGroup"]

    dictionary = { "Entrance":entrance, "Status":status, 
    "AuthenticationMethod":authtype,
    "Name":name, "AccessGroup":accessGroup, "datetimeScanned":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))
    }
    
    update("json/archivedTrans.json","actualVisitLogs",dictionary)
    update("json/pendingTrans.json","actualVisitLogs",dictionary)

#updates pendingTrans.json and send to backend 
#updates archivedTrans.json for backup 
def record_button(entrance,status):

    dictionary = { "Entrance":entrance, "Status":status, "datetimeScanned":datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))}

    update("json/archivedTrans.json","exitButtonPushes",dictionary)
    update("json/pendingTrans.json","exitButtonPushes",dictionary)

    
#update to update json files
def update(file,category,dictionary):

    #check if current json files exceed max length 
    clear_file_storage(file)

    with open(file,"r+") as outfile:
        try:
            data = json.load(outfile)
        except:
            data = { "controllerId": "","actualVisitLogs": [], "exitButtonPushes": []}
        
        data[category].append(dictionary)
        outfile.seek(0)

        json.dump(data,outfile,indent=4) 
    outfile.close()

    

#delete first half if exceeds length
def clear_file_storage(file):

     with open(file,"r") as checkfile:
        
        try:
            checkdata = json.load(checkfile)
        except:
            checkdata = { "controllerId": "","actualVisitLogs": [], "exitButtonPushes": []}

        if len(checkdata["actualVisitLogs"]) > MAX_JSON_LENGTH:
            checkfile.close()
            with open(file,"w+") as outfile:
                del checkdata["actualVisitLogs"][:(int(MAX_JSON_LENGTH/2))]
                json.dump(checkdata,outfile,indent=4) 

        if len(checkdata["exitButtonPushes"]) > MAX_JSON_LENGTH:
            checkfile.close()
            with open(file,"w+") as outfile:
                del checkdata["exitButtonPushes"][:(int(MAX_JSON_LENGTH/2))]
                json.dump(checkdata,outfile,indent=4) 

        else:
            checkfile.close()


def main():
    persondetails = {"Name": "YongNing","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}

    record_auth(persondetails,"Card","Maindoor","In")
    record_button("Maindoor","In")

    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","In")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","In")
    # record_auth(persondetails,"Card","Maindoor","In")
    # record_button("Maindoor","In")

if __name__ == "__main__":
    main()
