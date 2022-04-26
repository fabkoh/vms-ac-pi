import flask
import healthcheck
import json
from werkzeug.exceptions import BadRequest
import changeStatic
import os


app = flask.Flask(__name__)
app.config["DEBUG"] = True
path = os.path.dirname(os.path.abspath(__file__))

#get triggers healthcheck and send updated config file to backend 
#post checks for ip static ( set ip to static ) and Name, id, entranceName, pins, timeout, archivedmaxlength 



@app.route('/api/status')
def get_status():
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
        'E1 IN': readers_config['E1_IN'] == 'Connected',
        'E1 OUT': readers_config['E1_OUT'] == 'Connected',
        'E2 IN': readers_config['E2_IN'] == 'Connected',
        'E2 OUT': readers_config['E2_OUT'] == 'Connected'
    }

    return flask.Response(json.dumps(body), headers={ 'Content-type': 'application/json' })

app.run(host='0.0.0.0',port=5002,debug = True )
