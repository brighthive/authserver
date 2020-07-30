"""User API

An API for registering users with Auth Server.

"""

import json
from datetime import datetime

from flask import Blueprint
from flask_restful import Api, Resource, request

from authserver.db import DataTrust, DataTrustSchema, User, UserSchema, db, OAuth2Client, OAuth2Token
from authserver.utilities import ResponseBody, require_oauth


class UserDetailResource(Resource):
    """Details of the currently logged in user."""

    @require_oauth()
    def get(self):
        try:
            token = request.headers.get('authorization').split(' ')[1]
        except Exception:
            token = None

        if token:
            token_details = OAuth2Token.query.filter_by(access_token=token).first()
            if token_details:
                user_id = token_details.user_id
                user = User.query.filter_by(id=user_id).first()
                return {
                    'id': user.id,
                    'username': user.username,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'organization': {
                        'id': user.organization.id,
                        'name': user.organization.name
                    },
                    'email_address': user.email_address,
                    'telephone': user.telephone,
                    'active': user.active,
                    'data_trust_id': user.data_trust_id,
                    'date_created': str(user.date_created),
                    'date_last_updated': str(user.date_last_updated)
                }

        return {
            'firstname': 'Unknown',
            'lastname': 'Unknown'
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

    @require_oauth()
    def get(self, id: str = None):
        if not id:
            users = User.query.all()
            users_obj = self.users_schema.dump(users).data
            users_obj_clean = [{k: v for k, v in user.items() if k != 'organization_id'} for user in users_obj]
            return self.response_handler.get_all_response(users_obj_clean)
        else:
            user = User.query.filter_by(id=id).first()
            if user:
                user_obj = self.user_schema.dump(user).data
                user_obj.pop('organization_id')
                return self.response_handler.get_one_response(user_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    @require_oauth()
    def post(self, id: str = None):
        # Check for data, since all POST requests need it.
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()

        if id is not None:
            return self.response_handler.method_not_allowed_response()

        # Check for query params
        action = request.args.get("action")
        if action:
            try:
                user_id = request_data['id']
            except KeyError as e:
                return self.response_handler.custom_response(code=422, messages='Please provide the ID of the user.')
            else:
                if action == "deactivate":
                    return self._deactivate(user_id)
                else:
                    return self.response_handler.custom_response(code=422, messages="Invalid query param! 'action' can only be 'deactivate'.")

        data, errors = self.user_schema.load(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)
        try:
            user = User(request_data['username'], request_data['password'], firstname=request_data['firstname'], lastname=request_data['lastname'],
                        organization_id=request_data['organization_id'], email_address=request_data['email_address'],
                        data_trust_id=request_data['data_trust_id'])
            if 'telephone' in request_data.keys():
                user.telephone = request_data['telephone']
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('User', user.id, request_data)

    @require_oauth()
    def put(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self._update(id, False)

    @require_oauth()
    def patch(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        return self._update(id)

    @require_oauth()
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
            if hasattr(user, k) and k != 'password_hash':
                setattr(user, k, v)
            if k == 'password':
                user.password = v
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
        self._db_commit()

        clients = OAuth2Client.query.filter_by(user_id=user_id).all()
        for client in clients:
            client.client_secret = None
            self._db_commit()

        return self.response_handler.successful_update_response('User', user_id)

    def _db_commit(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name)


user_bp = Blueprint('user_ep', __name__)
user_api = Api(user_bp)
user_api.add_resource(UserResource, '/users', '/users/<string:id>')
user_api.add_resource(UserDetailResource, '/user')
