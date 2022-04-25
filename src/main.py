'''Starts the program'''
from api_to_etlas import post_config_to_etlas
from healthcheck import healthcheck
from system_calls import change_ip
import unicon
import api
from json_readers import Config, ConfigContainer

# start up script
# first set up ip ASSUMES PIS SHIP WITH DEFAULT IP
controller_config = ConfigContainer[0]['controllerConfig']
change_ip(controller_config['controllerIpStatic'] == 'static', controller_config['controllerIp'])

# do healthcheck and post config to etlas
unicon.set_readers_to_read()
healthcheck() # update Config
post_config_to_etlas()

# start program
unicon.main()
api.main()