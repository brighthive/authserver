"""Client API

An API for registering clients with Auth Server.

"""

import json
from uuid import uuid4
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.db import db, DataTrust, DataTrustSchema, User, UserSchema, OAuth2Client,\
    OAuth2ClientSchema, Role
from authserver.utilities import ResponseBody


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

    def post(self, id: str = None):
        if id is not None:
            return self.response_handler.method_not_allowed_response()
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()

        if not request_data:
            return self.response_handler.empty_request_body_response()
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

        The `client_secret` needs special attention, since it should NOT be changed arbitrarily. 
        Allow only two PATCH options: (1) delete the secret (i.e., disable the client), 
        or (2) rotate the secret – any other data PATCH'd as the client_secret should be ignored, and new secret generated. 
        This protects the Authserver from insecure secrets. 
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
                    if v is None:
                        client.client_secret = None
                    else:
                        client.client_secret = gen_salt(48)
                else:
                    setattr(client, k, v)
        try:
            db.session.commit()
            return self.response_handler.successful_update_response('Client', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)


client_bp = Blueprint('client_ep', __name__)
client_api = Api(client_bp)
client_api.add_resource(ClientResource, '/clients', '/clients/<string:id>')
