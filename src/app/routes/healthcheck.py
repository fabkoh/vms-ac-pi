from flask import Blueprint, Response
import src.healthcheck as healthcheck

healthcheck_bp = Blueprint('healthcheck', __name__)

@healthcheck_bp.route("/healthcheck", methods=["GET"])
def get_healthcheck() -> Response:
    healthcheck.main(True)
    return Response({}, status=204)
