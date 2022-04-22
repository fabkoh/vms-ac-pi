'''Contains the flask apis'''
from random import randint
import flask
import os
from json_readers import TestJson

app = flask.Flask(__name__)
app.config['DEBUG'] = (os.environ.get('FLASK_ENV', 'PRODUCTION') == 'DEVELOPMENT')

# # uncomment to test
@app.route('/test/change-json')
def change_test():
    TestJson.write({'a': randint(0, 100)})
    return flask.Response({}, 200, {'Content-type': 'application/json'})

def main():
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

if __name__ == '__main__':
    main()