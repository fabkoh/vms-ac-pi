# Python Program to SET IP Address to 250
# rmb to set dns to

import socket
import subprocess
#import psutil
import os
import netifaces


def get_default_gateway_windows():
    """Use netifaces module to get the default gateway."""
    try:
        import netifaces
        gws = netifaces.gateways()
        return gws['default'][netifaces.AF_INET][0]
    except:
        return None

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
            s.connect(('10.255.255.255', 1))
            hostIP = s.getsockname()[0]
    return hostIP

def get_netmask():
    for interface, data in psutil.net_if_addrs().items(): 
        addr = data[0]
        if interface == "eth0":
            return  addr.netmask
        #print('address  :', addr.address)
        #print('netmask  :', addr.netmask)
        #print('broadcast:', addr.broadcast)
        #print('---')
def get_gateway_ip():
        
    return system_call("ip r | grep default")




#def get_dns_servers():


print("Hostname:" + hostname)
processedIP = get_host_ip().split('.',1)[0] + "." + get_host_ip().split('.',2)[1] + "."+get_host_ip().split('.',3)[2] +".250"
print("host IP: " + get_host_ip())
print(get_default_gateway_windows())
print ("DNS: " + socket.getfqdn())
print ("Serial Num: " + get_serialnum().decode())
#print ("get_netmask():" + get_netmask())
def config_IP():

    os.system('sudo ifconfig eth0 down')

    #os.system('sudo ifconfig eth0 '+processedIP +' netmask '+ get_netmask())
    os.system('sudo ifconfig eth0 '+processedIP +' netmask 255.255.255.0')
    os.system('sudo ifconfig eth0 up')
    
    #os.system('sudo hostname uniCon' + '88')
    #to do:
    #get dns and configure dns as well
    
#config_IP()
stat = os.system('systemctl is-active startup.service')
if (stat) == 0:
   print ("starting Jar")
   #os.system('nohup java -jar -Dspring.profiles.active=production /home/pi/etlas/vms-ac-backend-0.0.1-SNAPSHOT.jar &')