import flask
import healthcheck
import json
from werkzeug.exceptions import BadRequest
import changeStatic
import os


app = flask.Flask(__name__)
app.config["DEBUG"] = True


#get triggers healthcheck and send updated config file to backend 
#post checks for ip static ( set ip to static ) and Name, id, entranceName, pins, timeout, archivedmaxlength 
@app.route('/config', methods=['GET','POST'])
def config():
    if flask.request.method == 'GET':
        try:
            healthcheck.main()
            healthcheck.update_server_config()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except:
            raise BadRequest('Error executing healthcheck')

    if flask.request.method == 'POST':
        content = flask.request.json
        config = content["controllerConfig"]
        try:
            healthcheck.main()
            file = "json/config.json"
            outfile = open(file)
            data = json.load(outfile)
            controllerConfig = data["controllerConfig"]
            if config["controllerSerialNo"] == controllerConfig["controllerSerialNo"] and config["controllerMAC"] == controllerConfig["controllerMAC"]:
                with open(file,"w") as writefile:
                    json.dump(content,writefile,indent=4) 
                    outfile.close()
                    
            if config["controllerIp"] != controllerConfig["controllerIp"] and config["controllerIpStatic"] == "True":
                changeStatic.change_static_ip(config["controllerIp"],changeStatic.get_default_gateway_windows(),"8.8.8.8")
                os.system('sudo ifconfig eth0 down')
                os.system('sudo ifconfig eth0 up')
                healthcheck.update_server_config()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except:
            raise BadRequest('Error updating config.json')


#update current file and  ( NOT DONE : restart program )
@app.route('/credOccur', methods=['POST'])
def credOccur():
    if flask.request.method == 'POST':
        content = flask.request.json
        try:
            entrance1 = content[0]["Entrance"]
            
        except:
            entrance1 = ""
        
        try:
            entrance2 = content[1]["Entrance"]
            
        except:
            entrance2 = ""
            
        try:
            file = "json/config.json"
            outfile = open(file)
            data = json.load(outfile)
            try:
                credEntrance1 = data["EntranceName"]["E1"]
            except:
                credEntrance1 = ""
            try:
                credEntrance2 = data["EntranceName"]["E2"]
            except:
                credEntrance2 = ""
                
            if (credEntrance1 == entrance1 and credEntrance2 == entrance2) or (credEntrance2 == entrance1 and credEntrance1 == entrance2):
                with open("json/credOccur.json","w") as writefile:
                    json.dump(content,writefile,indent=4) 
                    outfile.close()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        except:
            raise BadRequest('Error updating config.json')

app.run(host='0.0.0.0',port=5000,debug = True )