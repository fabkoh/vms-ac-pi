import socket
import subprocess
import time
import os
from config import IP_CONF_FILE
import netifaces

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

def restart_ifconfig():
    '''runs sudo ifconfig eth0 down, sudo ifconfig eth0 up'''
    os.system('sudo ifconfig eth0 down')
    os.system('sudo ifconfig eth0 up')

def check_if_static_ip():
    '''checks if pi's ip is static by reading /etc/dhcp.conf
    
    Returns:
        is_static_ip (bool)
    '''
    with open(IP_CONF_FILE, 'r') as f:
        data = f.readlines()
    
    return any(map(lambda l: l.startswith('static ip_address'), data))

def get_default_gateway_windows():
    """Use netifaces module to get the default gateway."""
    try:
        gws = netifaces.gateways()
        return gws['default'][netifaces.AF_INET][0]
    except:
        return None

def change_ip_to_static(ip_address, routers=None, dns='8.8.8.8'):
    routers = get_default_gateway_windows() if routers is None else routers
    try:
        with open(IP_CONF_FILE, 'r') as f:
            data = f.readlines()
            f.close()
        
        eth_index = None

        for i in range(len(data)):
            if 'interface eth0' in data[i]:
                eth_index = i
                break

        # if config is found, use index to edit the lines you need (the next 3)
        if eth_index:
            data[eth_index]   = 'eth0 interface\n'
            data[eth_index+1] = f'static ip_address={ip_address}/24\n'
            data[eth_index+2] = f'static routers={routers}\n'
            data[eth_index+3] = f'static domain_name_servers={dns}\n'

        with open(IP_CONF_FILE, 'w') as f:
            f.writelines(data)
            f.close()

        restart_ifconfig()
    except Exception as e:
        logging.exception("change_ip_to_static failed", e)
        

def change_ip_to_dynamic():
    try:
        with open(IP_CONF_FILE, 'r') as f:
            data = f.readlines()
            f.close()

            eth_index = None

            for i in range(len(data)):
                if 'interface eth0' in data[i]:
                    eth_index = i
                    break

            if eth_index is not None:
                # comment out the 4 lines
                for i in range(4):
                    data[eth_index+i] = '# ' + data[eth_index+i]

            with open(IP_CONF_FILE, 'w') as f:
                f.writelines(data)
                f.close()

            restart_ifconfig()
    except Exception as e:
        logging.exception('change_ip_to_dynamic failed', e)

def change_ip(ip_static, ip_address):
    '''changes ip, only if needed
    
    Args:
        ip_static  (bool):   if ip is static
        ip_address (string): new ip address
    '''
    curr_ip_static = check_if_static_ip()
    curr_ip_address = get_host_ip()

    # possible situations
    # 1) ip_static == curr_ip_static and curr_ip_address == ip_address
    #   => no change
    # 2) ip_static == curr_ip_static == false and curr_ip_address != ip_address
    #   => no change (cannot control dhcp ip)
    # 3) ip_static == curr_ip_static == true and curr_ip_address != ip_address
    #   => change to new ip
    # 4) ip_static != curr_ip_static
    #   => make_appropriate changes

    if ip_static and curr_ip_address != ip_address:
        # (3) and (4 when change to static ip)
        change_ip_to_static(ip_address)
    elif ip_static != curr_ip_static:
        # (4 when change to dchp)
        change_ip_to_dynamic()