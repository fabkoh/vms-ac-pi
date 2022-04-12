# Python Program to SET IP Address to 250
# rmb to set dns to

import socket
import subprocess
#import psutil
import os
import netifaces
import time 


hostname = socket.gethostname()   


def change_static_ip(ip_address, routers, dns):
    conf_file = '/etc/dhcpcd.conf'
    try:            
        # Sanitize/validate params above
        with open(conf_file, 'r') as file:
            data = file.readlines()

        # Find if config exists
        ethFound = next((x for x in data if 'interface eth0' in x), None)

        if ethFound:
            ethIndex = data.index(ethFound)
            if data[ethIndex].startswith('#'):
                data[ethIndex] = ('interface eth0\n') # commented out by default, make active

        # If config is found, use index to edit the lines you need ( the next 3)
        if ethIndex:
            data[ethIndex+1] = (f'static ip_address={ip_address}/24\n')
            data[ethIndex+2] = (f'static routers={routers}\n')
            data[ethIndex+3] = (f'static domain_name_servers={dns}\n')

        with open(conf_file, 'w') as file:
            file.writelines( data )

    except Exception as ex:
        logging.exception("IP changing error: %s", ex)
    finally:
        pass




def get_default_gateway_windows():
    """Use netifaces module to get the default gateway."""
    try:
        import netifaces
        gws = netifaces.gateways()
        return gws['default'][netifaces.AF_INET][0]
    except:
        return None




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

def get_gateway_ip():
        
    return system_call("ip r | grep default")

def set_env_variables():
    host_ip = str(get_host_ip)
    os.environ['DEVICE_IP']=host_ip
    os.environ['SECRET_ENCRYPTION_KEY'] = 'ISSSecretkey'

def run_servers():
    javacmd = 'java -jar "-Dspring.profiles.active=production" /home/pi/vms-ac-backend-0.0.1-SNAPSHOT.jar'
    postgrescmd = 'sudo service postgresql stop'
    os.system(javacmd)
    os.system(postgrescmd)


#def get_dns_servers():



#print ("get_netmask():" + get_netmask())
    

def main():
    print("Hostname:" + hostname)
    processedIP = get_host_ip().split('.',1)[0] + "." + get_host_ip().split('.',2)[1] + "."+get_host_ip().split('.',3)[2] +".250"
    print("host IP: " + get_host_ip())
    print(get_default_gateway_windows())
    print ("DNS: " + socket.getfqdn())
    print ("Serial Num: " + get_serialnum().decode())

    if get_host_ip() != processedIP:
        change_static_ip(processedIP,get_default_gateway_windows(),"8.8.8.8")
        os.system('sudo ifconfig eth down')
        os.system('sudo ifconfig eth up')


while True:
    try:
        main()
        break
    except:
        pass


while True:
    try:
        set_env_variables()
        break
    except:
        pass


while True:
    try:
        run_servers()
        break
    except:
        pass
   #os.system('nohup java -jar -Dspring.profiles.active=production /home/pi/etlas/vms-ac-backend-0.0.1-SNAPSHOT.jar &')