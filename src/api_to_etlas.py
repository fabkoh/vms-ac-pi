import requests
from config import ETLAS_DOMAIN
from json_readers import ConfigConatiner
import json

def post_config():
    url = ETLAS_DOMAIN + '/api/unicon/controller'
    
    config = ConfigConatiner[0]['controllerConfig']
    controller_id = config['controllerId'] or None
    controller_ip_static = config['controllerIpStatic']
    controller_ip = config['controllerIp']
    controller_mac = config['controllerMAC']
    controller_serial_number = config['controllerSerialNo']

    r = requests.post(
        url,
        data=json.dumps({
            'controllerId': controller_id,
            'controllerIP': controller_ip,
            'controllerIPStatic': controller_ip_static,
            'controllerMAC': controller_mac,
            'controllerSerialNo': controller_serial_number
        }),
        headers={ 'Content-type': 'application/json' },
        verify=False
    )

    print(r)
    print(r.status_code)
    print('SUCCESS' if r.status_code == 200 or r.status_code == 201 else 'FAIL')

if __name__ == '__main__':
    post_config()