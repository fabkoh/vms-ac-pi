import json
import os

path = os.path.dirname(os.path.abspath(__file__))

class FlaskConfig:
    ETLAS_DOMAIN = os.environ.get('ETLAS_DOMAIN', 'http://192.168.1.250:8082')

class DevConfig(FlaskConfig):
    DEBUG = True

class ProductionConfig(FlaskConfig):
    placeholder = 1

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

        if this dict is edited, remember to call update(self) to dump into filename 
        or the info in this class and filename would be different
        '''
        d = self._json
        for arg in args:
            d = d.get(arg, {})

        return d

    def update(self):
        '''Updates filename to self._json'''
        with open(self._filepath, 'w+') as outfile:
            json.dump(self._json, self._filepath, indent=4)
            outfile.close()
            # need to clear after?

class ControllerConfig(JsonConfig):
    '''Class used to access config.json'''
    def __init__(self):
        super().__init__(path + '/app/json/config.json')

flask_configs = {
    'development': DevConfig,
    'production': ProductionConfig
}


# configs to import
flask_config = flask_configs.get(os.environ.get('FLASK_ENV', 'production'), ProductionConfig)
controller_config = ControllerConfig()
