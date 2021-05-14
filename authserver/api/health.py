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
        key = b'''-----BEGIN PRIVATE KEY-----\nMIICXQIBADCCAjUGByqGSM44BAEwggIoAoIBAQD1D/ZP971imToMnUuy4Tj3NvYnmJBxLcn1cWxc4uYWnTT4f9qDry1RAKC9M5zgTcqZOA7uwEK+5uanwoSUCDD83gclOTbTPR96Ek92AEhiFZZflBrfyvnPoBy43VM/nQG1a/r7s+TpeHlW3jlbnYgjKZkq/IzxTv+0CcfDxV1suseMl64urDNEloJNiqqFIh7RpLsAB0FWnht53TUMR2XMTwnJw/sF4zWIISkq+SvAjQCEWIRzoO2WzLctB7mwIcZIS64j12x3N+1KcB7XFlVVfRKujPG5RucsNipPlvpYvvJ3eWyqurv9YtIpsHMOv8sH+xbA1qG2qXb6l2o8vQF/Ah0AuwLvc3rrJhr7+7DMagqqav4y08ywJ1AJg+psrQKCAQB2SIKqLXiUyCXsCU/csbfA9A85xCadh/LJurgF46Oyh/8B4b8oRsxuCu4Y6M2m27Sa0BL27qJi9VPjZo39OUihJpRoLIydjJHg6wcB11upmLc0glXMwQcyW648YZ87ypmWq7sJal2nPlQW97ny8dtxFtuNFWD1h3ZZbGNrjlvj02+dvWyzlYc9c/wPzVSXwHxtTQepcueU9orf/MVvVB0b+aKMuljJ2javrmIAHyawksYU3F9OP5bAjph0gPA31CGUmU+Qu/EpIjlga/pzS8/dsdfTNjw2c5XR5d8ZMIK/cRBvNT6lchNhXcQ6GNnpiKqOn90SLwg/TxXpOUYnpgjQBB8CHQCC5IvBISK+CCmFGky/T4RMM4LyZhwIKuzGkltz\n-----END PRIVATE KEY-----'''
        # jwt_lol = BrighthiveJWT(key).make_jwt({'wow': 1})
        import jwt
        jwt.encode({'wow':1}, key, algorithm="RS512")
        return self.config.get_app_status(), 200


health_api_bp = Blueprint('health_ep', __name__)
health_api = Api(health_api_bp)
health_api.add_resource(HealthCheckResource, '/health')
