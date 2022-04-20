import json
import os

path = os.path.dirname(os.path.abspath(__file__))

class FlaskConfig:
    print("flask config initialised")
    ETLAS_DOMAIN = 'http://192.168.1.250:8082'

class DevConfig(FlaskConfig):
    print("dev config initialised")
    DEBUG = True

class ProductionConfig(FlaskConfig):
    print("prod config initialised")

class JsonConfig:
    '''Helper class to read a maintain a json file'''
    def __init__(self, filepath):
        '''
        Args:
            filepath (string): the filepath to the json file
            
        Returns:
            json_config (JsonConfig object)
        '''
        self._filepath = filepath
        with open(filepath, "r+") as outfile:
            try:
                self._json = json.load(outfile)
            except:
                self._json = {}

    def read(self, *args):
        '''Helper method to read value in dict
        Args:
            args (any): the keys to reach a nested value

        Raises:
            TypeError: if trying to access the key of a non dict object

        Returns:
            value (any): the value reached by the keys, returns empty dict if keys not found
        '''
        d = self._json
        for arg in args:
            d = d.get(arg, {})

        return d

class ControllerConfig(JsonConfig):
    '''Class used to access config.json'''
    def __init__(self):
        super().__init__(path + '/app/json/config.json')

flask_configs = {
    'development': DevConfig,
    'production': ProductionConfig
}

flask_config = flask_configs.get(os.environ.get('FLASK_ENV', 'production'), ProductionConfig)

controller_config = ControllerConfig()
