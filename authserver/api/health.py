"""Healthcheck API

A simple API for returning health check information to clients.

"""

from flask import Blueprint, request
from flask_restful import Resource, Api
from injector import inject
from authserver.config import AbstractConfiguration
# from authserver.oauth2.rfc6749.authorization_server import BrighthiveJWT
from authserver.utilities import require_oauth


class HealthCheckResource(Resource):
    """A simple health check resource."""

    @inject
    def __init__(self, config: AbstractConfiguration):
        self.config = config

    def get(self):
        return self.config.get_app_status(), 200


health_api_bp = Blueprint('health_ep', __name__)
health_api = Api(health_api_bp)
health_api.add_resource(HealthCheckResource, '/health')
