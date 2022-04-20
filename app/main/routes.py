from . import main

@main.route('/')
def index():
    return "<p>Hello, World!</p>"