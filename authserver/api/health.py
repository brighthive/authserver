"""Healthcheck API

A simple API for returning health check information to clients.

"""

from flask import Blueprint, request
from flask_restful import Resource, Api
from authserver.config import Configuration

from authserver.utilities import require_oauth


class HealthCheckResource(Resource):
    """A simple health check resource."""

    def get(self):
        return Configuration.get_app_status(), 200


health_api_bp = Blueprint('health_ep', __name__)
health_api = Api(health_api_bp)
health_api.add_resource(HealthCheckResource, '/health')
