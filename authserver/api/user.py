"""User API

An API for registering users with Auth Server.

"""

from flask import Blueprint
from flask_restful import Resource, Api, request
from authserver.db import db, DataTrust, DataTrustSchema, User, UserSchema
from authserver.utilities import ResponseBody
from datetime import datetime


class UserResource(Resource):
    """A User Resource.

    This resource defines an Auth Service user who may have zero or more OAuth 2.0 clients
    associated with their accounts.

    """

    def __init__(self):
        self.data_trust_schema = DataTrustSchema()
        self.data_trusts_schema = DataTrustSchema(many=True)
        self.user_schema = UserSchema()
        self.users_schema = UserSchema(many=True)
        self.response_handler = ResponseBody()

    def get(self, id: str = None):
        return {'message': 'GET'}, 200

    def post(self, id: str = None):
        if id is not None:
            return self.response_handler.method_not_allowed_response()
        return {'message': 'POST'}, 201

    def put(self, id: str):
        return {'message': 'PUT'}, 200

    def patch(self, id: str):
        return {'message': 'PATCH'}, 200

    def delete(self, id: str):
        return {'message': 'DELETE'}, 200


user_bp = Blueprint('user_ep', __name__)
user_api = Api(user_bp)
user_api.add_resource(UserResource, '/users', '/users/<string:id>')
