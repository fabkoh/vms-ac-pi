import os
import netifaces

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
    
'''
change_static_ip("192.168.1.50", get_default_gateway_windows(), "8.8.8.8")
os.system('sudo ifconfig eth0 down')
'''
os.system('sudo ifconfig eth0 up')