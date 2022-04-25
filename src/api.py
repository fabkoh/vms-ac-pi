'''Contains the flask apis'''
import json
import flask
import os
from helpers import int_or_none
from json_readers import ConfigConatiner, Config
from system_calls import change_ip, check_if_static_ip, get_host_ip
from unicon import check_auth_device_status
from api_to_etlas import post_config_to_etlas

app = flask.Flask(__name__)
app.config['DEBUG'] = (os.environ.get('FLASK_ENV', 'PRODUCTION') == 'DEVELOPMENT')

@app.route('/api/unicon/status')
def get_status():
    '''Returns the unicon status
    
    Returns: (in response)
        body:
            controllerId           (int or null)
            controllerIP           (string)
            controllerIPStatic     (bool)
            controllerSerialNumber (string)
            controllerMAC          (string)
        status_code: 200
    '''
    body = check_auth_device_status()
    config = ConfigConatiner[0]['controllerConfig']
    body['controllerIPStatic'] = (config['controllerIpStatic'] != '')
    body['controllerIP']       = config['controllerIP']
    body['controllerId']       = int_or_none(config['controllerId'])
    body['controllerMAC']      = config['controllerMAC']
    return flask.Response(
        json.dumps(body),
        200,
        headers={ 'Content-type': 'application/json' }
    )

@app.route('/api/config', methods=['POST'])
def post_config():
    body = flask.request.json
    config = ConfigConatiner[0]
    controller_config = config['controllerConfig']

    assert(body['controllerSerialNumber'] == controller_config['controllerSerialNo'])

    # update ip if needed
    change_ip(body['controllerIPStatic'], body['controllerIP'])

    # update config
    controller_config['controllerIp'] = get_host_ip()
    controller_config['controllerIpStatic'] = check_if_static_ip()
    Config.write(config)

    post_config_to_etlas()

    return flask.Response({}, 204)

def main():
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

if __name__ == '__main__':
    main()