'''Provide classes to access json files'''
import json
import os

path = os.path.dirname(os.path.abspath(__file__))

def update(file_num):
    ''' updates the file containers

    Args:
        file_num(int): refer the the elif statement to see which file is updated
    '''
    if file_num == 0:
        ArchivedLogsConatiner[0] = ArchivedLogs.read()

    elif file_num == 1:
        ConfigConatiner[0] = Config.read()

    elif file_num == 2:
        CredOccurConatiner[0] = ArchivedLogs.read()

    elif file_num == 3:
        CredRulesSetConatiner[0] = ArchivedLogs.read()

    elif file_num == 4:
        EventActionTriggersConatiner[0] = ArchivedLogs.read()

    elif file_num == 5:
        PendingLogsConatiner[0] = ArchivedLogs.read()

    elif file_num == 6:
        StatusConatiner[0] = ArchivedLogs.read()

    elif file_num == 7:
        TestJsonContainer[0] = TestJson.read()

class JsonReader:
    def __init__(self, filename, file_num):
        '''JsonReader helper class to read from ./json folder
        
        Args:
            filename (string): the name of the file to read
            file_num (int):    refer to ./json_containers.py update() to see what file_num to input
        '''
        self._filename = filename
        self._content = None
        self._file_num = file_num
        self.read()

    # will explore using this method if performance is too slow
    # criteria: id(JsonReader) is the same in all files that import a JsonReader 
    # (to ensure information parity)
    # def get_content(self):
    #     return self._content

    def read(self):
        '''reads the json file
        
        Returns:
            content (Any): json content from file
        '''
        with open(self._filename) as file:
            self._content = json.load(file)
            file.close()

        return self._content

    def write(self, content):
        '''updates the json file
        
        Args:
            content (Any): updates the json file
        '''
        with open(self._filename, 'w') as file:
            json.dump(content, file, indent=4)
            self._content = content
            file.close()
        
        update(self._file_num)

# import the below objects to access json files
# remember to call write after changing the content of the object
ArchivedLogs       = JsonReader(path + '/json/archivedLogs.json'       , 0)
Config             = JsonReader(path + '/json/config.json'             , 1)
CredOccur          = JsonReader(path + '/json/credOccur.json'          , 2)
CredRulesSet       = JsonReader(path + '/json/credRulesSet.json'       , 3)
EventActionTrigger = JsonReader(path + '/json/eventActionTriggers.json', 4)
PendingLogs        = JsonReader(path + '/json/pendingLogs.json'        , 5)
Status             = JsonReader(path + '/json/status.json'             , 6)
TestJson           = JsonReader(path + '/json/test.json'               , 7)

# or import these containers, to get updated info call container[0] as demonstrated in main
ArchivedLogsConatiner        = [ArchivedLogs.read()]
ConfigConatiner              = [Config.read()]
CredOccurConatiner           = [CredOccur.read()]
CredRulesSetConatiner        = [CredRulesSet.read()]
EventActionTriggersConatiner = [EventActionTrigger.read()]
PendingLogsConatiner         = [PendingLogs.read()]
StatusConatiner              = [Status.read()]
TestJsonContainer            = [TestJson.read()]

# tests
if __name__ == '__main__':
    from random import randint

    # tests read and write
    test_object = { 'testNumber': randint(0, 100) }
    TestJson.write(test_object)
    assert(TestJson.read() == test_object)
    assert(TestJsonContainer == [test_object])

    print("SUCCESS")