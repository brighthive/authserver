"""User API

An API for registering users with Auth Server.

"""

import json
from datetime import datetime

from flask import Blueprint
from flask_restful import Api, Resource, request
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs

from authserver.db import DataTrust, DataTrustSchema, User, UserSchema, db, OAuth2Client
from authserver.utilities import ResponseBody

POST_ARGS = {
    'action': fields.Str(
        required=False,
        validate=validate.OneOf(['deactivate']),
    )
}

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
        if not id:
            users = User.query.all()
            users_obj = self.users_schema.dump(users).data
            return self.response_handler.get_all_response(users_obj)
        else:
            user = User.query.filter_by(id=id).first()
            if user:
                user_obj = self.user_schema.dump(user).data
                return self.response_handler.get_one_response(user_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)
    
    @use_args(POST_ARGS)
    def post(self, action, id: str = None):
        # Check for data, since all POST requests need it.
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()

        if id is not None:
            return self.response_handler.method_not_allowed_response()
        
        # Check for query params/webargs (i.e., action).
        if action:
            try:
                user_id = request_data['id']
            except KeyError as e:
                return self.response_handler.custom_response(code=422, messages='Please provide the ID of the user.')
            else:
                return self._deactivate(user_id)

        data, errors = self.user_schema.load(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)
        try:
            user = User(request_data['username'], firstname=request_data['firstname'], lastname=request_data['lastname'],
                        organization=request_data['organization'], email_address=request_data['email_address'],
                        data_trust_id=request_data['data_trust_id'])
            if 'telephone' in request_data.keys():
                user.telephone = request_data['telephone']
            else:
                user.telephone = 'N/A'
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('User', user.id, request_data)

    def put(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self._update(id, False)

    def patch(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        return self._update(id)

    def delete(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        try:
            user = User.query.filter_by(id=id).first()
            if user:
                user_obj = self.user_schema.dump(user).data
                db.session.delete(user)
                db.session.commit()
                return self.response_handler.successful_delete_response('User', id, user_obj)
            else:
                return self.response_handler.not_found_response(id)
        except Exception:
            return self.response_handler.not_found_response(id)

    def _update(self, id: str, partial=True):
        """General update function for PUT and PATCH.

        Using Marshmallow, the logic for PUT and PATCH differ by a single parameter. This method abstracts that logic
        and allows for switching the Marshmallow validation to partial for PATCH and complete for PUT.

        """
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        user = User.query.filter_by(id=id).first()
        if not user:
            return self.response_handler.not_found_response(id)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        data, errors = self.user_schema.load(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(user, k):
                setattr(user, k, v)
        try:
            user.date_last_updated = datetime.utcnow()
            db.session.commit()
            return self.response_handler.successful_update_response('User', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
    
    def _deactivate(self, user_id: str):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return self.response_handler.not_found_response(user_id)
        
        user.active = False

        clients = OAuth2Client.query.filter_by(user_id=user_id).all()

        print(clients, "!!!!")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name)

        return self.response_handler.successful_update_response('User', user_id)


user_bp = Blueprint('user_ep', __name__)
user_api = Api(user_bp)
user_api.add_resource(UserResource, '/users', '/users/<string:id>')
