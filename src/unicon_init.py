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

host_ip =   str(get_host_ip())
serial_num =  str(get_serialnum().decode())

print("host IP: " +host_ip)
print ("Serial Num: " + serial_num)



def update_ipaddress():
    url = 'http://192.168.1.250:8082/unicon/ipaddress'

    data = {"controllerIp":host_ip,"controllerSerialNo":serial_num}
    
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(data), headers=headers,verify=False)
    print(r)
    print(r.status_code)

    if r.status_code == 201 or r.status_code == 200:
        print("SUCCESS")

while True:
    try:
        update_ipaddress()
        break
    except:
        time.sleep(0.1)
