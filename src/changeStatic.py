import os
import netifaces
# main() does not run automatically as program (which imports this file) 
# already imported healthcheck
import healthcheck 

'''
interface wlan0
static ip_address=192.168.1.120/24
static routers=192.168.1.254
static domain_name_servers=192.168.1.254
'''


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

        restart_eth0()

    except Exception as ex:
        logging.exception("IP changing error: %s", ex)
    finally:
        pass


def restart_eth0():
    '''runs sudo ifconfig eth0 down sudo ifconfig eth0 up'''
    os.system('sudo ifconfig eth0 down')
    os.system('sudo ifconfig eth0 up')

def get_default_gateway_windows():
    """Use netifaces module to get the default gateway."""
    result = None
    while result == None:
        result = netifaces.gateways().get('default', {}).get(netifaces.AF_INET, [None])[0]
    return result   
    #try:
    #    import netifaces
    #    gws = netifaces.gateways()
    #    return gws['default'][netifaces.AF_INET][0]
   # except:
   #     return None
    
def change_dhcp():
    '''changes /etc/dhcpcd.conf to use dhcp'''
    with open('/etc/dhcpcd.conf', 'r') as f:
        data = f.readlines()
        f.close()

    eth_index = None
    for i in range(len(data)):
        if data[i].startswith('interface eth0'):
            eth_index = i
            break
    
    if eth_index: # if eth_index is None, should be dynamic, so no change
        # comment out 4 lines
        for i in range(4):
            data[eth_index+i] = '# ' + data[eth_index+i]

    with open('/etc/dhcpcd.conf', 'w') as f:
        f.writelines(data) # write changes
        f.close()

    restart_eth0()

def change_ip(static, ip_address):
    '''checks current ip and changes /etc/dhcpcd.conf if needed
    and then calls sudo ifconfig eth0 down sudo ifconfig eth0 up

    Args:
        static     (bool):   if ip is static
        ip_address (string): new ip (192.168.1.46 for example)
    '''

    curr_static = healthcheck.check_ip_static()
    curr_ip = healthcheck.get_host_ip()

    # possible situations:
    # static == True and (curr_static != static or ip_address != curr_ip)
    #   => change_static_ip
    # static == False and curr_static != static
    #   => change_dynamic_ip

    if static and (curr_static != static or ip_address != curr_ip):
        change_static_ip(ip_address, get_default_gateway_windows(), '8.8.8.8')
    elif (not static) and (curr_static != static):
        change_dhcp()

'''
change_static_ip("192.168.1.50", get_default_gateway_windows(), "8.8.8.8")
os.system('sudo ifconfig eth0 down')
'''
os.system('sudo ifconfig eth0 up')
