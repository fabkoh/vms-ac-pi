
import cv2
import json
import datetime

now = datetime.datetime.now()
timeString = now.strftime("%Y-%m-%d %H:%M")

# set up camera object
cap = cv2.VideoCapture(0)

# QR code detection object
detector = cv2.QRCodeDetector()

def store_json(newdata:dict):
    """Takes in a python dict and stores it as a .json file"""
    with open("/home/pi/file.json", "r+") as json_file:
        existingdata = json.load(json_file)
        existingdata.append(newdata)
        json_file.seek(0)
        json.dump(existingdata, json_file)
        
while True:
    # get the image
    _, img = cap.read()
    # get bounding box coords and data
    qrcode, bbox, _ = detector.detectAndDecode(img)
    authenticated = None
    # if there is a bounding box, draw one, along with the data
    if(bbox is not None):
        for i in range(len(bbox)):
            cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,
                     0, 255), thickness=2)
        cv2.putText(img, qrcode, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 255, 0), 2)
        if qrcode:
            #print("data found: ", data)
            #compare data against file
            #unlock
            file1 = open("/home/pi/codes.txt", "r")
            readfile = file1.read()
            if qrcode in readfile:
                authenticated = True
            file1.close()
  

            if authenticated:
                print("Authed!", qrcode)
                data = {}
                data["qrcode"] = qrcode
                data["datetime"] = timeString
                store_json(data)
                authenticated = None
                break
    # display the image preview
    cv2.imshow("code detector", img)
    if(cv2.waitKey(1) == ord("q")):
        break
# free camera object and exit
cap.release()
cv2.destroyAllWindows()

