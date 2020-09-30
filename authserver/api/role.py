"""Role API

An API for registering roles with Auth Server.

"""

from uuid import uuid4
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.db import db, Role, RoleSchema, AuthorizedScope, AuthorizedScopeSchema
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
            roles_obj = self.roles_schema.dump(roles)
            return self.response_handler.get_all_response(roles_obj)
        else:
            role = Role.query.filter_by(id=id).first()
            if role:
                role_obj = self.role_schema.dump(role)
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
        errors = self.role_schema.validate(request_data)
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
                role_obj = self.role_schema.dump(role)
                db.session.delete(role)
                db.session.commit()
                return self.response_handler.successful_delete_response('Role', id, role_obj)
            else:
                return self.response_handler.not_found_response(id)
        except Exception as e:
            print(e)
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
        errors = self.role_schema.validate(request_data, partial=partial)
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


class AuthorizedScopeResource(Resource):
    """Authorized scope resource for linking roles to scopes. """

    def __init__(self):
        self.authorized_scope_schema = AuthorizedScopeSchema()
        self.authorized_scopes_schema = AuthorizedScopeSchema(many=True)

        self.response_handler = ResponseBody()

    @require_oauth()
    def get(self, id: str = None, sid: str = None):
        if sid is None:
            try:
                authorized_scopes = AuthorizedScope.query.all()
                scopes_obj = self.authorized_scopes_schema.dump(authorized_scopes)
                scopes_obj_clean = [{k: v for k, v in authorized_scope.items() if k != 'scope_id' and k != 'role_id' and k != 'role'} for authorized_scope in scopes_obj]
                return self.response_handler.get_all_response(scopes_obj_clean)
            except Exception:
                return self.response_handler.exception_response('Unknown')
        else:
            try:
                authorized_scope = AuthorizedScope.query.filter(
                    AuthorizedScope.role_id == id, AuthorizedScope.scope_id == sid).first()
                scope_obj = self.authorized_scope_schema.dump(authorized_scope)
                scope_obj.pop('role_id', None)
                scope_obj.pop('scope_id', None)
                if scope_obj:
                    return self.response_handler.get_one_response(scope_obj)
                else:
                    return self.response_handler.not_found_response(id=sid)
            except Exception:
                return self.response_handler.exception_response('Unkown')

    @require_oauth()
    def post(self, id: str = None, sid: str = None):
        if sid is not None:
            return self.response_handler.method_not_allowed_response()

        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()
        errors = self.authorized_scope_schema.validate(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            authorized_scope = AuthorizedScope(role_id=id, scope_id=request_data['scope_id'])
            db.session.add(authorized_scope)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('AuthorizedScope', authorized_scope.role_id, request_data)

    @require_oauth()
    def put(self, id: str = None, sid: str = None):
        return self.response_handler.method_not_allowed_response()

    @require_oauth()
    def patch(self, id: str = None, sid: str = None):
        return self.response_handler.method_not_allowed_response()

    @require_oauth()
    def delete(self, id: str, sid: str = None):
        if sid is None:
            return self.response_handler.method_not_allowed_response()
        try:
            authorized_scope = AuthorizedScope.query.filter(AuthorizedScope.role_id == id, AuthorizedScope.scope_id == sid).first()
            if authorized_scope:
                authorized_scope_obj = self.authorized_scope_schema.dump(authorized_scope)
                db.session.delete(authorized_scope)
                db.session.commit()
                return self.response_handler.successful_delete_response('Role', id, authorized_scope_obj)
            else:
                return self.response_handler.not_found_response(sid)
        except Exception:
            return self.response_handler.not_found_response(sid)


role_bp = Blueprint('role_ep', __name__)
role_api = Api(role_bp)
role_api.add_resource(RoleResource, '/roles', '/roles/<string:id>')
role_api.add_resource(AuthorizedScopeResource, '/roles/<string:id>/scopes', '/roles/<string:id>/scopes/<string:sid>')
