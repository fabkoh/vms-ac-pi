import json
import os

path = os.path.dirname(os.path.abspath(__file__))

class Config:
    ETLAS_DOMAIN = os.environ.get('ETLAS_DOMAIN', 'http://192.168.1.250:8082')

class DevConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    placeholder = 1

class JsonReader:
    '''Helper class to read a maintain a json file'''
    def __init__(self, filepath):
        '''
        Args:
            filepath (string): the filepath to the json file
            
        Returns:
            json_reader (JsonReader object)
        '''
        self._filepath = filepath
        with open(filepath, "r+") as outfile:
            try:
                self._json = json.load(outfile)
            except:
                self._json = {}

    def read(self):
        '''Helper method to read value in dict
        Returns:
            value (any): the value reached by the keys, returns empty dict if keys not found

        if the returned object is edited, remember to call JsonReader.update() to dump into filename 
        or the info in this class and filename would be different
        '''
        return self._json

    def update(self, new_json):
        '''Updates filename to self._json'''
        with open(self._filepath, 'w+') as outfile:
            json.dump(new_json, self._filepath, indent=4)
            outfile.close()
            # need to clear after?

        self._json = new_json

flask_configs = {
    'development': DevConfig,
    'production': ProductionConfig
}


# configs to import
FlaskConfig = flask_configs.get(os.environ.get('FLASK_ENV', 'production'), ProductionConfig)
ControllerConfig    = JsonReader(path + '/app/json/config.json')
CredentialConfig    = JsonReader(path + '/app/json/credOccur.json')
PendingLogs         = JsonReader(path + '/app/json/pendingLogs.json')
EventActionTriggers = JsonReader(path + '/json/eventActionTriggers.json')