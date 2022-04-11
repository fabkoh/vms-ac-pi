
import pigpio
import json
from datetime import datetime
# Python Program to Get IP Address and send to server 250
import socket
import subprocess
#import psutil
import os
import json
import requests
import time

hostname = socket.gethostname()   


def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()

def get_serialnum():
    return system_call("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2")

def get_mac():
    return system_call("cat /sys/class/net/eth0/address")

def get_host_ip(hostIP=None):
    if hostIP is None or hostIP == 'auto':
        hostIP = 'ip'

    if hostIP == 'dns':
        hostIP = socket.getfqdn()
    elif hostIP == 'ip':
        from socket import gaierror
        try:
            hostIP = socket.gethostbyname(socket.getfqdn())
        except gaierror:
            logger.warn('gethostbyname(socket.getfqdn()) failed... trying on hostname()')
            hostIP = socket.gethostbyname(socket.gethostname())
        if hostIP.startswith("127."):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # doesn't have to be reachable
            while True:
                try:
                    s.connect(('10.255.255.255', 1))
                    hostIP = s.getsockname()[0]
                    break
                except:
                    time.sleep(0.1)

    return hostIP

def main():

    pi = pigpio.pi()
    fileconfig = open('json/config.json')
    config = json.load(fileconfig)



    GPIOpins = config["GPIOpins"]

    E1_IN_D0= int(GPIOpins["E1_IN_D0"])
    E1_IN_D1= int(GPIOpins["E1_IN_D1"])
    pi.set_mode(E1_IN_D0, pigpio.INPUT)
    pi.set_mode(E1_IN_D1, pigpio.INPUT)

    E1_OUT_D0= int(GPIOpins["E1_OUT_D0"])
    E1_OUT_D1= int(GPIOpins["E1_OUT_D1"])
    pi.set_mode(E1_OUT_D0, pigpio.INPUT)
    pi.set_mode(E1_OUT_D1, pigpio.INPUT)

    E2_IN_D0= int(GPIOpins["E2_IN_D0"])
    E2_IN_D1= int(GPIOpins["E2_IN_D1"])
    pi.set_mode(E2_IN_D0, pigpio.INPUT)
    pi.set_mode(E2_IN_D1, pigpio.INPUT)

    E2_OUT_D0= int(GPIOpins["E2_OUT_D0"])
    E2_OUT_D1= int(GPIOpins["E2_OUT_D1"])
    pi.set_mode(E2_OUT_D0, pigpio.INPUT)
    pi.set_mode(E2_OUT_D1, pigpio.INPUT)

    def test_for_connection(D0,D1,reader):
        if pi.read(D0) == 1 and pi.read(D1) == 1:
            readersConnection[reader] = "Connected"
        else:
            readersConnection[reader] = ""



    file = "json/config.json"
    with open(file,"r+") as outfile:
        try:
            data = json.load(outfile)
        except:
            data = []
        
        readersConnection = data["controllerConfig"]["readersConnection"]
        test_for_connection(E1_IN_D0,E1_IN_D1,"E1_IN")
        test_for_connection(E2_IN_D0,E2_IN_D1,"E2_IN")
        test_for_connection(E1_OUT_D0,E1_OUT_D1,"E1_OUT")
        test_for_connection(E2_OUT_D0,E2_OUT_D1,"E2_OUT")

        now = datetime.now()
        current_date_time = now.strftime("%d-%m-%Y %H:%M:%S")
        readersConnection["dateAndTime"] = current_date_time
        
        host_ip =   str(get_host_ip())
        serial_num =  str(get_serialnum().decode())
        mac =  str(get_mac().decode())
        data["controllerConfig"]["controllerIp"] = host_ip
        data["controllerConfig"]["controllerSerialNo"] = serial_num[:-1]
        data["controllerConfig"]["controllerMAC"] = mac[:-1]
        


        outfile.seek(0)
        json.dump(data,outfile,indent=4) 
        outfile.close()



def update_ipaddress():
        url = 'http://192.168.1.250:8082/unicon/config'
        file = "json/config.json"
        with open(file,"r+") as outfile:
            try:
                data = json.load(outfile)
            except:
                data = []
        
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(data), headers=headers,verify=False)
        print(r)
        print(r.status_code)

        if r.status_code == 201 or r.status_code == 200:
            print("SUCCESS")
            
def update_server_config():
    while True:
        try:
            update_ipaddress()
            break
        except:
            time.sleep(0.1)


def set_env_variables():
    host_ip = str(get_host_ip())
    os.environ['DEVICE_IP']=host_ip
    os.environ['SECRET_ENCRYPTION_KEY']='ISSSecretkey'

main()
update_server_config()
set_env_variables()

