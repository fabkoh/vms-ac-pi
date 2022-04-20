import json
from config import pending_logs, flask_config

def update_server_events():
    url = flask_config.ETLAS_DOMAIN + '/unicon/event'

    try:
        pass
        # r = requests.post(url,
        #                   json.dump(pending_logs.read()),
        #                   headers={ 'Content-type': 'application/json' },
        #                   verify=False,
        #                   timeout=0.5)
        # print(r)
        # print(r.status_code)

        # if 200 <= r.status_code <= 201:
        #     print("SUCCESS")
        #     pending_logs.update([]) # clear pending logs
    except:
        print("No connection to ", url)

def update_external_zone_status(controller_id, entrance, dictionary, direcion):
    pass