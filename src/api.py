'''Contains the flask apis'''
import flask
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = (os.environ['FLASK_ENV'] == 'DEVELOPMENT')

