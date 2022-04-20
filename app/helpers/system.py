from datetime import datetime
import socket
import subprocess
import time
from config import flask_config, controller_config
import json
import pigpio

def system_call(command):
    '''Helper method to run command on a unix terminal
    
    Args:
        command (string): the command to execute

    Returns:
        bytes (bytes): the output of the command (convert to string with str(bytes.decode()))
    '''
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()

def get_serial_number():
    '''Helper method to read serial number from unix terminal
    
    Returns:
        serial_number (bytes): the serial number in bytes
    '''
    return system_call("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2")

def get_mac_address():
    '''Helper method to return mac address from unix terminal
    
    Returns:
        mac_address (bytes): the mac address in bytes
    '''
    return system_call("cat /sys/class/net/eth0/address")

def get_host_ip(dns_enabled=True):
    '''Helper method to return host ip
    
    Args:
        dns_enabled (boolean): true if dns is enabled on machine
        
    Returns:
        host_ip (string): the host ip string
    '''
    if dns_enabled:
        return socket.getfqdn()

    from socket import gaierror
    try:
        host_ip = socket.gethostbyname(socket.getfqdn())
    except gaierror:
        # logger.warn('socket.gethostbyname(socket.getfqdn()) failed...\ntrying socket.gethostbyname(socket.hostname())')
        host_ip = socket.gethostbyname(socket.gethostname())
    if host_ip.startswith('127.'): # private ip i think
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # doesn't have to be reachable
        while True:
            try:
                s.connect(('10.255.255.255', 1))
                host_ip = s.getsockname()[0]
                break
            except:
                time.sleep(0.1)
    return str(host_ip)

def update_ip_address():
    '''???'''
    url = flask_config.ETLAS_DOMAIN + '/unicon/config'
    # r = requests.post(url, 
    #                   data=json.dump(controller_config.read()),
    #                   headers={ 'Content-type': 'application/json' }
    #                   verify=False)
    # print(r)
    # print(r.status_code)

    # if 200 <= r.status_code <= 201:
    #     print("update_pi_address(): SUCCESS")

def healthcheck():
    pi = pigpio.pi()
    controller_config_json = controller_config.read()
    gpio_pins = controller_config_json['GPIOpins']

    pins = [] #stores the pin numbers
    for entrance in ('E1_', 'E2_'):
       for direction in ('IN_', 'OUT_'):
           for data in ('D0', 'D1'):
               pins.append(int(gpio_pins[entrance+direction+data]))

    for pin in pins:
        pi.set_mode(pin, pigpio.INPUT)

    readers_connection = controller_config_json['controllerConfig']['readersConnection']
    auth_device_types = ['E1_IN', 'E1_OUT', 'E2_IN', 'E2_OUT'] # in same order as pins
    # update connection status
    for i in range(4):
        readers_connection[auth_device_types[i]] = \
            "Connected" if \
            (pi.read(pins[i*2]) and pi.read(pins[i*2+1])) else \
            ""

    # last updated
    readers_connection["dateAndTime"] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    controller_info = controller_config_json['controllerConfig']
    controller_info['controllerIp'] = get_host_ip()
    controller_info['controllerSerialNo'] = str(get_serial_number().decode())[:-1]
    controller_info['controllerMAC'] = str(get_mac_address().decode())[:-1]

    # commit changed to json file
    controller_config.update(controller_config_json)

    while True:
        try:
            update_ip_address()
            break
        except:
            time.sleep(1)