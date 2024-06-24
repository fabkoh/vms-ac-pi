from flask import Blueprint, Response, request, abort
import json
import src.healthcheck as healthcheck
from src.app.utils.helpers import load_json, save_json
from src.app.utils.locks import config_lock
import src.events as events
import src.program as program

api_bp = Blueprint('api', __name__)

@api_bp.route("/status", methods=["GET"])
def get_status() -> Response:
    """Returns healthcheck info"""
    healthcheck.main()
    with config_lock:
        data = load_json("config.json")
    controller_config = data["controllerConfig"]
    readers_config = controller_config["readersConnection"]
    body = {
        "controllerId": controller_config["controllerId"] or None,
        "controllerIP": controller_config["controllerIp"],
        "controllerIPStatic": controller_config["controllerIPStatic"],
        "controllerMAC": controller_config["controllerMAC"],
        "controllerSerialNo": controller_config["controllerSerialNo"],
        "E1_IN": readers_config["E1_IN"] == "Connected",
        "E1_OUT": readers_config["E1_OUT"] == "Connected",
        "E2_IN": readers_config["E2_IN"] == "Connected",
        "E2_OUT": readers_config["E2_OUT"] == "Connected",
    }
    return Response(json.dumps(body), mimetype='application/json', status=200)

@api_bp.route("/unlock/entrance/<int:entrance_id>", methods=["GET"])
def unlock_entrance(entrance_id: int) -> Response:
    events.open_door_using_entrance_id(entrance_id)
    return Response({}, status=200)

# Add other routes similarly
