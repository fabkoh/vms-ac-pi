'''Starts the program'''
from api_to_etlas import post_config_to_etlas
from healthcheck import healthcheck
import unicon
import api
from json_readers import Config, ConfigConatiner

# first set up Config
unicon.set_readers_to_read()
healthcheck() # update Config
print(ConfigConatiner[0])
post_config_to_etlas() # post config to etlas

unicon.main()
api.main()