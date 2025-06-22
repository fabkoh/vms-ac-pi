print("healthcheck before imports")

import pigpio
import json
from datetime import datetime
# Python Program to Get IP Address and send to server 250
import socket
import subprocess
# import psutil
import os
import json
import requests
import time
import gc
from changeStatic import *
import GPIOconfig
from var import server_url
from lock import config_lock
# change_static_ip, get_default_gateway_windows

print("healthcheck after imports")

path = os.path.dirname(os.path.abspath(__file__))
file = path+"/json/config.json"

pi = GPIOconfig.pi
config = None


def update_config():
    global config
    with config_lock:
        fileconfig = open(file)
        config = json.load(fileconfig)
        fileconfig.close()


update_config()  # initial load of file

GPIOpins = config["GPIOpins"]

E1_IN_D0 = int(GPIOpins["E1_IN_D0"])
E1_IN_D1 = int(GPIOpins["E1_IN_D1"])
pi.set_mode(E1_IN_D0, pigpio.INPUT)
pi.set_mode(E1_IN_D1, pigpio.INPUT)

E1_OUT_D0 = int(GPIOpins["E1_OUT_D0"])
E1_OUT_D1 = int(GPIOpins["E1_OUT_D1"])
pi.set_mode(E1_OUT_D0, pigpio.INPUT)
pi.set_mode(E1_OUT_D1, pigpio.INPUT)

E2_IN_D0 = int(GPIOpins["E2_IN_D0"])
E2_IN_D1 = int(GPIOpins["E2_IN_D1"])
pi.set_mode(E2_IN_D0, pigpio.INPUT)
pi.set_mode(E2_IN_D1, pigpio.INPUT)

E2_OUT_D0 = int(GPIOpins["E2_OUT_D0"])
E2_OUT_D1 = int(GPIOpins["E2_OUT_D1"])
pi.set_mode(E2_OUT_D0, pigpio.INPUT)
pi.set_mode(E2_OUT_D1, pigpio.INPUT)


def check_ip_static():
    '''checks /etc/dhcpcd.conf to see if ip is static'''
    with open('/etc/dhcpcd.conf', 'r') as f:
        data = f.readlines()

    # checks if any of the strings start with 'static ip_address'
    return any(map(lambda s: s.startswith('static ip_address'), data))


def system_call(command):
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()


def get_host_ip(hostIP=None):
    print("Healthcheck get_host_ip started")
    if hostIP is None or hostIP == 'auto':
        hostIP = 'ip'

    if hostIP == 'dns':
        hostIP = socket.getfqdn()

    elif hostIP == 'ip':
        print("Healthcheck get_host_ip in elif block for ip")
        from socket import gaierror
        print("Healthcheck get_host_ip before trycatch block")
        try:
            print("Healthcheck get_host_ip in try part")
            hostIP = socket.gethostbyname(socket.getfqdn())
        except gaierror:
            print("Healthcheck get_host_ip in catch part")
            logger.warn(
                'gethostbyname(socket.getfqdn()) failed... trying on hostname()')
            hostIP = socket.gethostbyname(socket.gethostname())
        print("Healthcheck get_host_ip after trycatch block")

        print("Host IP is: " + str(hostIP))

        print("Healthcheck get_host_ip before 127 block")
        if hostIP.startswith("127."):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # doesn't have to be reachable
            print("Healthcheck get_host_ip before while loop")
            while True:
                try:
                    s.connect(('10.255.255.255', 1))
                    hostIP = s.getsockname()[0]
                    break
                except:
                    time.sleep(0.1)
            print("Healthcheck get_host_ip after while loop")
        print("Healthcheck get_host_ip after 127 block")

        print("Host IP is: " + str(hostIP))

        print("Healthcheck get_host_ip before 169.264 block")
        if str(hostIP).startswith('169.254') and (not check_ip_static()):  # apipa, use static ip
            change_static_ip(
                '192.168.1.230', get_default_gateway_windows(), '8.8.8.8')
            return get_host_ip('ip')
        print("Healthcheck get_host_ip after 169.264 block")

    return str(hostIP)


def main(post_to_etlas=False):
    print("Healthcheck started")

    hostname = socket.gethostname()

    print("Healthcheck start method definitions")
    def get_serialnum():
        return system_call("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2")

    def get_mac():
        return system_call("cat /sys/class/net/eth0/address")

    def post_to_etlas():
        url = server_url+'/api/unicon/controller'

        with open(file, "r+") as outfile:
            data = json.load(outfile)
            outfile.close()

        headers = {'Content-type': 'application/json'}
        controllerConfig = data['controllerConfig']
        readersConfig = controllerConfig['readersConnection']
        body = {
            'controllerId': controllerConfig['controllerId'] or None,
            # ip updated already below before this function call
            'controllerIP': controllerConfig['controllerIp'],
            'controllerIPStatic': check_ip_static(),
            'controllerMAC': controllerConfig['controllerMAC'],
            'controllerSerialNo': controllerConfig['controllerSerialNo'],
            'E1_IN': readersConfig['E1_IN'] == 'Connected',
            'E1_OUT': readersConfig['E1_OUT'] == 'Connected',
            'E2_IN': readersConfig['E2_IN'] == 'Connected',
            'E2_OUT': readersConfig['E2_OUT'] == 'Connected'
        }
        r = requests.post(url, data=json.dumps(
            body), headers=headers, verify=False)

        # print(r)
        # print(r.status_code)

        if r.status_code == 201 or r.status_code == 200:
            print("SUCCESS")

        try:
            r2 = requests.post(url, data=json.dumps(
                body), headers=headers, verify=False)
            r2.raise_for_status()  # raise an HTTPError if status code is not 200
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def test_for_connection(D0, D1, reader):
        if pi.read(D0) == 1 and pi.read(D1) == 1:
            readersConnection[reader] = "Connected"
        else:
            readersConnection[reader] = ""
    print("Healthcheck end method definitions")

    print("Healthcheck open file block started")
    with open(file, "w+") as outfile:
        print("Healthcheck before json load try catch block")
        try:
            data = json.load(outfile)
        except:
            data = []
        print("Healthcheck after json load try catch block")

        print("Healthcheck before test_for_connection calls")
        readersConnection = config["controllerConfig"]["readersConnection"]
        test_for_connection(E1_IN_D0, E1_IN_D1, "E1_IN")
        test_for_connection(E2_IN_D0, E2_IN_D1, "E2_IN")
        test_for_connection(E1_OUT_D0, E1_OUT_D1, "E1_OUT")
        test_for_connection(E2_OUT_D0, E2_OUT_D1, "E2_OUT")
        print("Healthcheck after test_for_connection calls")

        print("Healthcheck before datetime update")
        now = datetime.now()
        current_date_time = now.strftime("%d-%m-%Y %H:%M:%S")
        readersConnection["dateAndTime"] = current_date_time
        print("Healthcheck after datetime update")

        print("Healthcheck before host information update")
        print("Healthcheck before get_host_ip call")
        host_ip = str(get_host_ip())
        print("Healthcheck after get_host_ip call")
        serial_num = str(get_serialnum().decode())
        mac = str(get_mac().decode())
        config["controllerConfig"]["controllerIp"] = host_ip
        config["controllerConfig"]["controllerSerialNo"] = serial_num[:-1]
        config["controllerConfig"]["controllerMAC"] = mac[:-1]
        print("Healthcheck after host information update")

        print("Healthcheck before config outfile dump")
        outfile.seek(0)
        json.dump(config, outfile, indent=4)
        outfile.close()
        print("Healthcheck after config outfile dump")

    print("Healthcheck open file block completed")

    if post_to_etlas:
        while True:
            try:
                post_to_etlas()
                break
            except:
                time.sleep(0.1)
    
    print("Healthcheck completed")
