from flask import Flask, jsonify, request #import objects from the Flask model
app = Flask(__name__) #define app using Flask
import datetime
#import webapp3
import json

now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M")

#def main(qrCode):
    
                          
@app.route('/', methods=['GET'])
def main():
    #scannedRecord = [{'qrCode' : webapp3.data}, {'Time' : timeString}, {'flag' : '1'}]
    return jsonify({'Scanned Records' : scannedRecord})



@app.route('/testjsonconfig', methods=['POST'])
def processtest():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        rawjson = request.json
        js = jsonify(rawjson) # is a dict
        pairs = rawjson.items()

        for key, value in pairs:
            if (key == "controllerIP") and (value == "192.168.1.166"):
                print ("sameip")
            else:
                print("run os commands to configure")
        return js
    else:
        return 'Content-Type not supported!'
    
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=True)
       #authenticated = None