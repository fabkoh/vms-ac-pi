import os

from flask import Blueprint, Response
from src.app import change_static
from src import healthcheck

control_bp = Blueprint("control", __name__)

@control_bp.route("/reset", methods=["POST"])
def post_reset():
    '''
    Resets the controller. Resets ip to 192.168.1.67. 
    then posts new config to etlas
    '''
    change_static.change_ip(False, '192.168.1.67')
    healthcheck.main(True) # post new config to etlas
    return Response({}, status=200)


@control_bp.route("/reboot", methods=["POST"])
def post_reboot() -> Response:
    """Reboots the controller"""
    os.system("sudo reboot")
    return Response({}, status=200)


@control_bp.route("/shutdown", methods=["POST"])
def post_shutdown() -> Response:
    """Shuts down the controller"""
    change_static.change_dhcp()
    os.system("sudo halt")
    return Response({}, status=200)
