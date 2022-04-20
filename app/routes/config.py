from flask import jsonify
from . import routes
from app.helpers.system import healthcheck
from werkzeug.exceptions import BadRequest

@routes.route('/config')
def get_config():
    try:
        # healthcheck()
        # update_server_config()

        response = jsonify({'success': True})
        response.status_code = 200
        return response
    except:
        raise BadRequest('Error executing healthcheck')