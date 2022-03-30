from flask import Blueprint

cred = Blueprint('cred',__name__)

@cred.route('/')
def home():
    return "<h1>Test</h1>"


