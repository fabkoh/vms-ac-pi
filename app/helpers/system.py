import socket
import subprocess
import time
from config import flask_config

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
    url = flask_config.ETLAS_DOMAIN + '/unicon/config'
    print(url)
