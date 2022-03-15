import json
from datetime import datetime 



def record_auth(persondetails,authtype,entrance,status):
    name = persondetails["Name"]
    accessGroup = persondetails["AccessGroup"]

    dictionary = { "Entrance":entrance, "Status":status, 
    "AuthenticationMethod":authtype,
    "Name":name, "AccessGroup":accessGroup, "datetimeScanned":datetime.now().strftime(("%m/%d/%Y %H:%M:%S"))
    }
    print(dictionary)

    with open("archivedTrans.json","r+") as outfile:
        try:
            data = json.load(outfile)
        except:
            data = { "controllerId": "","actualVisitLogs": [], "exitButtonPushes": []}
            
        
        data["actualVisitLogs"].append(dictionary)
        print(data)
        outfile.seek(0)
        json.dump(data,outfile,indent=4)



    # with open("archivedTrans.json","a") as outfile:
    #     json.dump(dictionary,outfile,indent=4)
    




# methods to check status 
# when all tgt, trigger something
# execute, dynamic function, async await for API
# 
persondetails = {"Name": "YongNing","diffpassword" : "NO", "AccessGroup": "ISS","Schedule":"Schedule"}

record_auth(persondetails,"Card","Maindoor","In")