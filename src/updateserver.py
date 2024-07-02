from datetime import datetime

from executor import thread_pool_executor
from var import server_url
import json
import requests
import os
import threading

from lock import pending_logs_lock
import logging

# Create a logger
logger = logging.getLogger(__name__)

# Set the level of logging. It can be DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.setLevel(logging.DEBUG)

# Create a file handler for outputting log messages to a file
home = os.path.expanduser("~")
file_handler_path = home + "/UpdateServer.log"
file_handler = logging.FileHandler(file_handler_path)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)

path = os.path.dirname(os.path.abspath(__file__))


def update_server_events():
    with pending_logs_lock:
        with open(path+"/json/pendingLogs.json", 'r') as file:
            data = json.load(file)

    url = server_url + '/api/unicon/events'

    logger.info("Update Server Events called")
    # Start the send_request_to_server function in a new thread

    thread_pool_executor.submit(send_request_to_server, url, data)

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
