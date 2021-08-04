
from flask import Flask, jsonify, request, render_template #import objects from the Flask model
app = Flask(__name__) #define app using Flask
import datetime
import webapp3
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 



now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M")

#def main(qrCode):

                          
@app.route('/', methods=['GET'])
def main():
    scannedRecord = [{'qrCode' : ""}, {'Time' : timeString}, {'flag' : '1'}]
    #return jsonify({'Scanned Records' : scannedRecord})
    templateData = {'title' : "",
                    'qrcode' :webapp3.data,
                    'time' : timeString}
    return render_template('index.html', **templateData)
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=True)
       #authenticated = None
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        print("Button was pushed!")
        result = usbrelay_py.board_control(board[0],1,1)
        time.sleep(3)
        result = usbrelay_py.board_control(board[0],1,0)
