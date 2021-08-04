from flask import Flask, jsonify, request #import objects from the Flask model
app = Flask(__name__) #define app using Flask
import datetime
import webapp3

now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M")

#def main(qrCode):
    
                          
@app.route('/', methods=['GET'])
def main():
    scannedRecord = [{'qrCode' : webapp3.data}, {'Time' : timeString}, {'flag' : '1'}]
    return jsonify({'Scanned Records' : scannedRecord})

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=True)
       #authenticated = None