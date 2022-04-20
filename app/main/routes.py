from . import main
from ...helpers.system import update_ip_address

@main.route('/')
def index():
    print('test')
    update_ip_address()
    return "<p>Hello, World!</p>"