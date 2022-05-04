import flask
import healthcheck
import json
from werkzeug.exceptions import BadRequest
import changeStatic
import os


app = flask.Flask(__name__)
app.config["DEBUG"] = True
path = os.path.dirname(os.path.abspath(__file__))

@app.route('/api/status')
def get_status():
    '''returns healthcheck info
    
    Returns: (response)
        code: 200
        body: {
            controllerId       (int or null): 1
            controllerIP       (string):      192.168.1.46
            controllerIPStatic (bool):        true
            controllerMAC      (string):      e4:5f:01:25:85:f3
            controllerSerialNo (string):      100000005a46e105
            'E1_IN'            (bool):        false
            'E1_OUT'           (bool):        false
            'E2_IN'            (bool):        true
            'E2_OUT'           (bool):        true
        }
    '''
    healthcheck.main(False)
    with open(path + '/json/config.json', 'r') as f:
        data = json.load(f)
        f.close()

    controller_config = data['controllerConfig']
    readers_config = controller_config['readersConnection']
    body = {
        'controllerId': controller_config['controllerId'] or None,
        'controllerIP': controller_config['controllerIp'],
        'controllerIPStatic': healthcheck.check_ip_static(),
        'controllerMAC': controller_config['controllerMAC'],
        'controllerSerialNo': controller_config['controllerSerialNo'],
        'E1_IN': readers_config['E1_IN'] == 'Connected',
        'E1_OUT': readers_config['E1_OUT'] == 'Connected',
        'E2_IN': readers_config['E2_IN'] == 'Connected',
        'E2_OUT': readers_config['E2_OUT'] == 'Connected'
    }

    return flask.Response(json.dumps(body), headers={ 'Content-type': 'application/json' })

@app.route('/api/config', methods=['POST'])
def post_config():
    '''changes config.json and post changes to etlas, 
    aborts if controllerSerialNo is different
    
    Args (request):
        body: {
            controllerIPStatic  (bool):   true
            controllerIP        (string): 192.168.1.46
            controllerSerialNo  (string): 100000005a46e105
        }
        
    Returns (response):
        code: 200
    '''
    request_body = flask.request.json
    with open(path + '/json/config.json', 'r') as f:
        data = json.load(f)
        f.close()
    # check if this is the intended controller
    assert(request_body['controllerSerialNo'] == data['controllerConfig']['controllerSerialNo'])

    changeStatic.change_ip(request_body['controllerIPStatic'], request_body['controllerIP'])
    healthcheck.main() # post new config to etlas
    return flask.Response({}, 204)

@app.route('/api/reset', methods=['POST'])
def post_reset():
    '''Resets the controller. Resets ip to 192.168.1.67. then posts new config to etlas
    
    Returns (response):
        code: 200
    '''
    changeStatic.change_ip(True, '192.168.1.67')
    healthcheck.main() # post new config to etlas
    return flask.Response({}, 204)

@app.route('/api/reboot', methods=['POST'])
def post_reboot():
    '''reboots the controller'''
    os.system('sudo reboot')

@app.route('/api/shutdown', methods=['POST'])
def post_shutdown():
    '''shutdowns the controller'''
    os.system('sudo halt')


app.run(host='0.0.0.0',port=5000,debug = True )
