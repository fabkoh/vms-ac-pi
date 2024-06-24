import os

from flask import Blueprint, Response
from src.app import change_static

control_bp = Blueprint("control", __name__)


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
