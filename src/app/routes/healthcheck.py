from flask import Blueprint, Response

from src import healthcheck

healthcheck_bp = Blueprint("healthcheck", __name__)


@healthcheck_bp.route("/healthcheck", methods=["GET"])
def get_healthcheck() -> Response:
    healthcheck.main(True)
    return Response({}, status=204)
