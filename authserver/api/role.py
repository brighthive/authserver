"""Role API

An API for registering roles with Auth Server.

"""

import json
from uuid import uuid4
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.db import db, DataTrust, DataTrustSchema, User, UserSchema, OAuth2Client,\
    OAuth2ClientSchema, Role, RoleSchema
from authserver.utilities import ResponseBody, require_oauth


class RoleResource(Resource):
    """Role Resource

    This resource represents a role associated with a client.

    """

    def __init__(self):
        self.role_schema = RoleSchema()
        self.roles_schema = RoleSchema(many=True)
        self.response_handler = ResponseBody()

    @require_oauth()
    def get(self, id: str = None):
        if not id:
            roles = Role.query.all()
            roles_obj = self.roles_schema.dump(roles).data
            return self.response_handler.get_all_response(roles_obj)
        else:
            role = Role.query.filter_by(id=id).first()
            if role:
                role_obj = self.role_schema.dump(role).data
                return self.response_handler.get_one_response(role_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    @require_oauth()
    def post(self, id: str = None):
        if id is not None:
            return self.response_handler.method_not_allowed_response()
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()
        data, errors = self.role_schema.load(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            role = Role(role=request_data['role'], description=request_data['description'])
            if 'rules' in request_data.keys():
                role.rules = request_data['rules']
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Role', role.id, request_data)

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
            role = Role.query.filter_by(id=id).first()
            if role:
                role_obj = self.role_schema.dump(role).data
                db.session.delete(role)
                db.session.commit()
                return self.response_handler.successful_delete_response('Role', id, role_obj)
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
        role = Role.query.filter_by(id=id).first()
        if not role:
            return self.response_handler.not_found_response(id)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        data, errors = self.role_schema.load(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(role, k):
                setattr(role, k, v)
        try:
            db.session.commit()
            return self.response_handler.successful_update_response('Role', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)


role_bp = Blueprint('role_ep', __name__)
role_api = Api(role_bp)
role_api.add_resource(RoleResource, '/roles', '/roles/<string:id>')
