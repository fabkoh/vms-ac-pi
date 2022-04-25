import socket
import subprocess
import time
from config import IP_CONF_FILE

def system_call(command):
    '''Helper to run system command and return the output
    
    Args:
        command (string): command to execute on the terminal
        
    Returns:
        output (bytes): output of the executed command
    '''
    p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
    return p.stdout.read()

def get_serial_number():
    '''Helper to return serial number of device'''
    return system_call("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2")

def get_mac_address():
    '''Helper to return MAC address'''
    return system_call('cat /sys/class/net/eth0/address')

def get_host_ip(dns_enabled=False):
    '''returns the host ip
    
    Args:
        dns_enabled (bool): if dns is enabled
        
    Returns:
        host ip (string): host ip
    '''
    if dns_enabled:
        return socket.getfqdn()
    else: # look for ip instead
        try:
            host_ip = socket.gethostbyname(socket.getfqdn())
        except socket.gaierror:
            logger.warn('socket.gethostbyname(socket.getfqdn()) failed...\ntrying socket.gethostbyname(socket.gethostname())')
            host_ip = socket.gethostbyname(socket.gethostname())

        if host_ip.startswith('127.'): # private ip, not connected to internet
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while True:
                try:
                    s.connect(('10.255.255.255', 1))
                    host_ip = s.getsockname()[0]
                    break
                except:
                    time.sleep(0.1)

            return str(host_ip)

def check_if_static_ip():
    '''checks if pi's ip is static by reading /etc/dhcp.conf
    
    Returns:
        is_static_ip (bool)
    '''
    with open(IP_CONF_FILE, 'r') as f:
        data = f.readlines()
    
    return any(map(lambda l: l.startswith('static ip_address'), data))