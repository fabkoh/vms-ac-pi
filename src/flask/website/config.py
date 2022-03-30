from flask import Blueprint, request, Response
import json

config = Blueprint('config',__name__)

@config.route('/controller_config',methods=['POST'])
def controllerconfig():
    #try and read, if not exist, write config file, if exist, check if controllerId and controllerSerialNo is the same
    # if same, replace existing file 

    newdata = request.json
    if newdata:
        try:
            with open("src/json/sample.json","r") as outfile:
                try:
                    data = json.load(outfile)
                except:
                    data = {}
        except:
            pass
                # for visitlogs in newdata["actualVisitLogs"]:  
                #     data["actualVisitLogs"].append(visitlogs)
                #     newdata["actualVisitLogs"].remove(visitlogs)

                # for exitlogs in newdata["exitButtonPushes"]:  
                #     data["exitButtonPushes"].append(exitlogs)
                #     newdata["exitButtonPushes"].remove(exitlogs)
                
                # print(data)
                # print("---------------------------")
                # print(newdata)

                # outfile.seek(0)
                # json.dump(data,outfile,indent=4) 

    return Response(status=201)

@config.route('/status',methods=['POST'])
def status():
    fileconfig = open('config.json')
    config = json.load(fileconfig)

    newdata = request.json
    if newdata:
        with open("status.json","r") as outfile:
            try:
                data = json.load(outfile)
            except:
                data = {"controllerId": "222222", "E1": [],"E2": [] }

            controllerEntrance=""
            direction = newdata["Direction"]
            try:
                if newdata["E1"]:
                    controllerEntrance = "E1"
            except:
                pass
            try:
                if newdata["E2"]:
                    controllerEntrance = "E2"
            except:
                pass

        with open("status.json","w+") as outfile:   
            try:
                for controllerInZone in config["ZoneStatus"]["controllersInZoneE1"]:
                    if controllerInZone["controllerId"] == newdata["controllerId"] and controllerInZone["Entrance"] == controllerEntrance:
                        if direction == "In":
                            data["E1"].append(newdata["E1"][0])
                        if direction == "Out":
                            data["E1"].remove(newdata["E1"][0])
            except:
                pass
            try:
                for controllerInZone in config["ZoneStatus"]["controllersInZoneE2"]:
                    if controllerInZone["controllerId"] == newdata["controllerId"] and controllerInZone["Entrance"] == controllerEntrance:
                        if direction == "In":
                            data["E2"].append(newdata["E2"][0])
                        if direction == "Out":
                            data["E2"].remove(newdata["E2"][0])
            except:
                pass
           
            outfile.seek(0)
            json.dump(data,outfile,indent=4) 

    return "<p>ok</p>"

@config.route('/copy',methods=['POST'])
def copy():
    new = request.json
    with open("copy.json","w+") as outfile:
        json.dump(new,outfile,indent=4) 