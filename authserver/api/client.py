"""Client API

An API for registering clients with Auth Server.

"""

import json
import time
from datetime import datetime
from uuid import uuid4

from flask import Blueprint
from flask_restful import Api, Resource, request
from werkzeug.security import gen_salt

from authserver.db import (OAuth2Client, OAuth2ClientSchema, Role, User, UserSchema, db)
from authserver.utilities import ResponseBody, require_oauth


class ClientResource(Resource):
    """Client Resource

    This resource represents an OAuth 2.0 client that is associated with a user.

    """

    def __init__(self):
        self.client_schema = OAuth2ClientSchema()
        self.clients_schema = OAuth2ClientSchema(many=True)
        self.response_handler = ResponseBody()

    @require_oauth()
    def get(self, id: str = None):
        if not id:
            clients = OAuth2Client.query.all()
            clients_obj = self.clients_schema.dump(clients)
            return self.response_handler.get_all_response(clients_obj)
        else:
            client = OAuth2Client.query.filter_by(id=id).first()
            if client:
                client_obj = self.client_schema.dump(client)
                return self.response_handler.get_one_response(client_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    @require_oauth()
    def post(self, id: str = None):
        '''
        The POST method mainly enables the following:
        (1) creation of a new Client.
        (2) deletion or rotatation of the secret of an existing client – accomplished by POSTing with 
        query params (?action=delete_secret, or ?action=rotate_secret).
        '''

        # Check for data, since all POST requests need it.
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()

        # Check for query params
        action = request.args.get("action")
        if action:
            try:
                client_id = request_data['id']
            except KeyError as e:
                return self.response_handler.custom_response(code=422, messages='Please provide the ID of the client.')

            if action == 'delete_secret':
                return self._delete_secret(client_id)
            elif action == 'rotate_secret':
                return self._rotate_secret(client_id)
            else:
                return self.response_handler.custom_response(code=422, messages="Invalid query param! 'action' must be either 'delete_secret' or 'rotate_secret'.")

        # Assume that the request intends to create a new user: an ID should not be in the request data.
        if id is not None:
            return self.response_handler.method_not_allowed_response()

        errors = self.client_schema.validate(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            client = OAuth2Client()
            client.id = str(uuid4()).replace('-', '')
            client.user_id = request_data['user_id']
            client.client_id = gen_salt(24)
            client.client_secret = gen_salt(48)
            client_metadata = {'scope': ''}
            for k, v in request_data.items():
                if hasattr(client, k):
                    if k == 'roles':
                        try:
                            for role_id in request_data[k]:
                                role = Role.query.filter_by(id=role_id).first()
                                if role:
                                    client.roles.append(role)
                                else:
                                    return self.response_handler.custom_response(code=400, messages={'roles': ['Error assigning role to client.']})
                        except Exception as e:
                            return self.response_handler.custom_response(code=400, messages={'roles': ['Error assigning role to client.']})
                    else:
                        try:
                            setattr(client, k, v)
                        except Exception as e:
                            client_metadata[k] = v
            client.set_client_metadata(client_metadata)
            client.client_id_issued_at = int(time.time())

            db.session.add(client)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Client', client.id, request_data)

    @require_oauth()
    def put(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self.update(id, False)

    @require_oauth()
    def patch(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        return self.update(id)

    @require_oauth()
    def delete(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        try:
            client = OAuth2Client.query.filter_by(id=id).first()
            if client:
                client_obj = self.client_schema.dump(client)
                db.session.delete(client)
                db.session.commit()
                return self.response_handler.successful_delete_response('Client', id, client_obj)
            else:
                return self.response_handler.not_found_response(id)
        except Exception:
            return self.response_handler.not_found_response(id)

    def update(self, id: str, partial=True):
        """General update function for PUT and PATCH.

        Using Marshmallow, the logic for PUT and PATCH differ by a single parameter. This method abstracts that logic
        and allows for switching the Marshmallow validation to partial for PATCH and complete for PUT.
        """
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        client = OAuth2Client.query.filter_by(id=id).first()
        if not client:
            return self.response_handler.not_found_response(id)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        errors = self.client_schema.validate(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(client, k):
                if k == 'roles':
                    try:
                        if len(request_data[k]) == 0:  # allow removal of all roles
                            client.roles = []
                        else:
                            current_roles = client.roles.copy()
                            new_roles = []
                            for role_id in request_data[k]:
                                role = Role.query.filter_by(id=role_id).first()
                                if role:
                                    new_roles.append(role)
                                    if role not in client.roles:  # only append roles that aren't already there
                                        client.roles.append(role)
                                else:
                                    return self.response_handler.custom_response(code=400, messages={'roles': ['Error assigning role to client.']})
                            for role in current_roles:
                                if role not in new_roles:
                                    client.roles.remove(role)
                    except Exception as e:
                        return self.response_handler.custom_response(code=400, messages={'roles': ['Error assigning role to client.']})
                elif k == 'client_secret':
                    return self.response_handler.custom_response(code=422, messages={'client_secret': ['The client_secret cannot be updated.']})
                else:
                    setattr(client, k, v)
        try:
            db.session.commit()
            return self.response_handler.successful_update_response('Client', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)

    def _update_secret(self, client_id: str, new_secret):
        """Helper function for updating the client_secret.

        This function serves the delete and rotate actions, available in the POST method.

        """
        client = OAuth2Client.query.filter_by(id=client_id).first()
        if not client:
            return self.response_handler.not_found_response(client_id)

        client.client_secret = new_secret

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name)
        return self.response_handler.custom_response(
            code=200,
            status='OK',
            messages={'client_secret': new_secret}
        )

    def _delete_secret(self, client_id):
        new_secret = None
        return self._update_secret(client_id, new_secret)

    def _rotate_secret(self, client_id):
        new_secret = gen_salt(48)
        return self._update_secret(client_id, new_secret)


client_bp = Blueprint('client_ep', __name__)
client_api = Api(client_bp)
client_api.add_resource(ClientResource, '/clients', '/clients/<string:id>')
