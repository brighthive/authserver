"""Client API

An API for registering clients with Auth Server.

"""

import json
from datetime import datetime
from uuid import uuid4

from flask import Blueprint
from flask_restful import Api, Resource, request
from werkzeug.security import gen_salt
# from webargs import fields, validate
# from webargs.flaskparser import use_args, use_kwargs

from authserver.db import (DataTrust, DataTrustSchema, OAuth2Client,
                           OAuth2ClientSchema, Role, User, UserSchema, db)
from authserver.utilities import ResponseBody

# POST_ARGS = {
#     'action': fields.Str(
#         required=False,
#         validate=validate.OneOf(['delete_secret', 'rotate_secret']),
#     ),
# }

class ClientResource(Resource):
    """Client Resource

    This resource represents an OAuth 2.0 client that is associated with a user.

    """

    def __init__(self):
        self.client_schema = OAuth2ClientSchema()
        self.clients_schema = OAuth2ClientSchema(many=True)
        self.response_handler = ResponseBody()

    def get(self, id: str = None):
        if not id:
            clients = OAuth2Client.query.all()
            clients_obj = self.clients_schema.dump(clients).data
            return self.response_handler.get_all_response(clients_obj)
        else:
            client = OAuth2Client.query.filter_by(id=id).first()
            if client:
                client_obj = self.client_schema.dump(client).data
                return self.response_handler.get_one_response(client_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    # @use_args(POST_ARGS)
    # def post(self, action, id: str = None):
    def post(self, id: str = None):
        # All POSTs should have data. Check for this.
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()

        # Some POSTs have query params.
        # if action:
        #     try:
        #         client_id = request_data['id']
        #     except KeyError as e:
        #         return self.response_handler.custom_response(code=422, messages='Please provide the ID of the client.')

        #     if action['action'] == 'delete_secret':
        #         return self._delete_secret(client_id)
        #     elif action['action'] == 'rotate_secret':
        #         return self._rotate_secret(client_id)

        if id is not None:
            return self.response_handler.method_not_allowed_response()
        
        data, errors = self.client_schema.load(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            client = OAuth2Client()
            client.id = str(uuid4()).replace('-', '')
            client.user_id = request_data['user_id']
            client.client_id = gen_salt(24)
            client.client_secret = gen_salt(48)
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
                        setattr(client, k, v)
            db.session.add(client)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Client', client.id, request_data)

    def put(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self.update(id, False)

    def patch(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        return self.update(id)

    def delete(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        try:
            client = OAuth2Client.query.filter_by(id=id).first()
            if client:
                client_obj = self.client_schema.dump(client).data
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
        data, errors = self.client_schema.load(request_data, partial=partial)
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
        return self.response_handler.successful_update_response('Client', client_id)

    def _delete_secret(self, client_id):
        new_secret = None
        return self._update_secret(client_id, new_secret)
    
    def _rotate_secret(self, client_id):
        new_secret = gen_salt(48)
        return self._update_secret(client_id, new_secret)
    

client_bp = Blueprint('client_ep', __name__)
client_api = Api(client_bp)
client_api.add_resource(ClientResource, '/clients', '/clients/<string:id>')
