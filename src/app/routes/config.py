from flask import Blueprint, Response, abort, request

from src import changeStatic, events, eventsMod, GPIOconfig, healthcheck, relay
from src.app.utils.helpers import load_json, save_json
from src.app.utils.locks import config_lock

config_bp = Blueprint("config", __name__)


@config_bp.route("/config", methods=["POST"])
def post_config() -> Response:
    """Changes config.json and post changes to etlas"""
    request_body = request.json
    if not all(key in request_body for key in
               ["controllerIPStatic", "controllerIP", "controllerSerialNo"]):
        abort(400)

    with config_lock:
        data = load_json("config.json")

    if (request_body["controllerSerialNo"]
            != data["controllerConfig"]["controllerSerialNo"]):
        abort(400)

    changeStatic.change_ip(request_body["controllerIPStatic"],
                           request_body["controllerIP"])
    healthcheck.main(True)
    update_config()
    return Response({}, status=204)


def update_config():
    """Helper method to update config"""
    events.update_config()
    eventsMod.update_config()
    GPIOconfig.update_config()
    healthcheck.update_config()
    relay.update_config()
