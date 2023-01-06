import json
import requests
import os
path = os.path.dirname(os.path.abspath(__file__))
from var import server_url

def update_server_events():
    url = server_url+'/api/unicon/events'

    file = open(path+"/json/pendingLogs.json") 
    data = json.load(file)
    #print("11-here")
    
    try:
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers,verify=False,timeout =0.5)
        print(r)
        print(r.status_code)

        if r.status_code == 201 or r.status_code == 200:
            print("SUCCESS")
            fileclear = open(path+'/json/pendingLogs.json', 'w')
            json.dump([],fileclear,indent=4) 
            fileclear.close()
    except:
        print("No connection to ",url)
        
#dictionary = {"Name": "Bryan","AccessGroup": "ISS"}
#entrance = E1/ E2

def update_external_zone_status(controllerId, entrance, dictionary,direction):
    while True:
        break
        url = 'http://127.0.0.1:5000/status'

        data = {"controllerId": controllerId,
               entrance: [dictionary],
               "Direction":direction}

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)

        print(r.status_code)

        if r.status_code == 200:
            break

        else:
            break
        


#update_server_events()
#update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"In")
#update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"Out")
