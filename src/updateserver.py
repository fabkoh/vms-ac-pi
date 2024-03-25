from datetime import datetime
from var import server_url
import json
import requests
import os
import threading

from lock import pending_logs_lock

path = os.path.dirname(os.path.abspath(__file__))


def update_server_events():
    print("inside update_server_events ", str(datetime.now()))
    
    print("outside pending logs lock ", str(datetime.now()))
    with pending_logs_lock:
        print("inside pending logs lock ", str(datetime.now()))
        with open(path+"/json/pendingLogs.json", 'r') as file:
            data = json.load(file)
        print("after pending logs lock ", str(datetime.now()))

    url = server_url + '/api/unicon/events'
    # Start the send_request_to_server function in a new thread
    thread = threading.Thread(target=send_request_to_server, args=(url, data))
    thread.setDaemon(True)
    thread.start()
    print("inside update_server_events ", str(datetime.now()))

    # The function returns immediately, while the thread continues to run


def send_request_to_server(url, data):
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=0.5)
        print(response)
        print(response.status_code)
        if response.status_code in (201, 200):
            print("SUCCESS")
            with pending_logs_lock:
                with open(path + '/json/pendingLogs.json', 'w') as fileclear:
                    json.dump([], fileclear, indent=4)
    except Exception as e:
        print("No connection to ", url, "\nError: ", e)


def update_external_zone_status(controllerId, entrance, dictionary, direction):
    while True:
        break
        url = 'http://127.0.0.1:5000/status'

        data = {"controllerId": controllerId,
                entrance: [dictionary],
                "Direction": direction}

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, data=json.dumps(data), headers=headers)

        print(r.status_code)

        if r.status_code == 200:
            break

        else:
            break


# update_server_events()
# update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"In")
# update_external_zone_status("123456","E1",{"Name": "YongNing","AccessGroup": "ISS"},"Out")
