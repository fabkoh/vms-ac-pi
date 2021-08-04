import cv2
from flask import Flask, jsonify, request #import objects from the Flask model
app = Flask(__name__) #define app using Flask
import datetime

now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M")

# set up camera object
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

while True:
    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    data, bbox, _ = detector.detectAndDecode(img)
    authenticated = None
    # if there is a bounding box, draw one, along with the data
    if(bbox is not None):
        for i in range(len(bbox)):
            cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                     0, 255), thickness=2)
        cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        if data:
            #print("data found: ", data)
            #compare data against file
            #unlock
            file1 = open("/home/pi/codes.txt", "r")
            readfile = file1.read()
            if data in readfile:
               authenticated = True
            file1.close()

            if authenticated:

               print("Authed!", data) 
               scannedRecord = [{'qrCode' : data}, {'Time' : timeString}, {'flag' : '1'}]
               break
               
    # display the image preview
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break
  

@app.route('/', methods=['GET'])
def test():
    return jsonify({'Scanned Records' : scannedRecord})
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=8080, debug=True)
       #authenticated = None

# free camera object and exit
cap.release()
cv2.destroyAllWindows()  


#@app.route('/lang', methods=['GET'])
#def returnAll():
#	return jsonify({'languages' : languages})

#@app.route('/lang/<string:name>', methods=['GET'])
#def returnOne(name):
#	langs = [language for language in languages if language['name'] == name]
#	return jsonify({'language' : langs[0]})

#@app.route('/lang', methods=['POST'])
#def addOne():
#	language = {'name' : request.json['name']}
#	languages.append(language)
#	return jsonify({'languages' : languages})

#if __name__ == "__main__":
#   app.run(host='0.0.0.0', port=8080, debug=True)
