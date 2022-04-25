import datetime
import time
from api_to_etlas import post_config_to_etlas
from system_calls import check_if_static_ip, get_host_ip, get_mac_address, get_serial_number
from unicon import check_auth_device_status
from json_readers import Config, ConfigContainer

def healthcheck():
    '''Checks for pi's mac address, ip, ip static, serial number and writes to Config
    
    Note:
        require pi's pins to be initialised
    '''
    config = ConfigContainer[0]

    auth_device_status = check_auth_device_status()
    auth_device_config = config['controllerConfig']['readersConnection']

    auth_device_config['E1_IN']  = 'connected' if auth_device_status['E1IN']  else ''
    auth_device_config['E1_OUT'] = 'connected' if auth_device_status['E1OUT'] else ''
    auth_device_config['E2_IN']  = 'connected' if auth_device_status['E2IN']  else ''
    auth_device_config['E2_OUT'] = 'connected' if auth_device_status['E2OUT'] else ''

    now = datetime.datetime.now()
    auth_device_config['dateAndTime'] = now.strftime('%d-%m-%Y %H:%M:%S')

    controller_config = config['controllerConfig']
    controller_config['controllerIp']           = get_host_ip()
    controller_config['controllerIpStatic']     = 'static' if check_if_static_ip() else ''
    controller_config['controllerSerialNumber'] = str(get_serial_number().decode())[:-1]
    controller_config['controllerMAC']          = str(get_mac_address().decode())[:-1]

    Config.write(config)

