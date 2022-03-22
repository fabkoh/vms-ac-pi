import json
import requests


def update_server_trans():
    url = 'http://127.0.0.1:5000/transLog'

    file = open('json/pendingTrans.json') 
    data = json.load(file)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)

    print(r.status_code)

    if r.status_code == 200:
        print("SUCCESS")
        open('json/pendingTrans.json', 'w').close()

#dictionary = {"Name": "Bryan","AccessGroup": "ISS"}
#entrance = E1/ E2

def update_external_zone_status(controllerId, entrance, dictionary,direction):
    while True:
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
        


update_server_trans()
#update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"In")
#update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"Out")