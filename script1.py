import json

url = 'http://192.168.1.125:5000/copy'

file = open('test.json') 
data = json.load(file)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

print(r.status_code)
