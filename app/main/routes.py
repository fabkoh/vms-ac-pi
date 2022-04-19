from . import main

@main.route('/', methods=['GET'])
def index():
    return "<p>Hello, World!</p>"