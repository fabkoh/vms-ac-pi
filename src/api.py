import flask
import healthcheck
import json
from werkzeug.exceptions import BadRequest


app = flask.Flask(__name__)
app.config["DEBUG"] = True


#get triggers healthcheck and send updated config file to backend 
#post checks for ip static ( set ip to static ) and Name, id, entranceName, pins, timeout, archivedmaxlength 
@app.route('/config', methods=['GET','POST'])
def config():
    if flask.request.method == 'GET':
        try:
            print("here")
            healthcheck.main()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except:
            raise BadRequest('Error executing healthcheck')

    if flask.request.method == 'POST':
        content = flask.request.json
        try:
            file = "json/config.json"
            outfile = open(file)
            data = json.load(outfile)
            controllerConfig = data["controllerConfig"]
            if content["controllerSerialNo"] == controllerConfig["controllerSerialNo"] and content["controllerMAC"] == controllerConfig["controllerMAC"]:
                with open(file,"w+") as writefile:
                    json.dump(content,writefile,indent=4) 
                    outfile.close()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except:
            raise BadRequest('Error updating config.json')



@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"




app.run()