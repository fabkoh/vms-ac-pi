'''Starts the program'''
from api_to_etlas import post_config
from healthcheck import healthcheck
import unicon
import api
from json_readers import Config, ConfigConatiner

# first set up Config
unicon.set_readers_to_read()
healthcheck() # update Config
post_config() # post config to etlas

unicon.main()
api.main()