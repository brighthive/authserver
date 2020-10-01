"""Scope API

An API for registering scopes with Auth Server.

"""

from uuid import uuid4
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.db import db, Scope, ScopeSchema
from authserver.utilities import ResponseBody, require_oauth


class ScopeResource(Resource):
    """Scope Resource

    This resource represents a scope associated with a client.

    """

    def __init__(self):
        self.scope_schema = ScopeSchema()
        self.scopes_schema = ScopeSchema(many=True)
        self.response_handler = ResponseBody()

    @require_oauth()
    def get(self, id: str = None):
        if not id:
            scopes = Scope.query.all()
            scopes_obj = self.scopes_schema.dump(scopes)
            return self.response_handler.get_all_response(scopes_obj)
        else:
            scope = Scope.query.filter_by(id=id).first()
            if scope:
                scope_obj = self.scope_schema.dump(scope)
                return self.response_handler.get_one_response(scope_obj, request={'id': id})
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
        errors = self.scope_schema.validate(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            scope = Scope(scope=request_data['scope'], description=request_data['description'])
            db.session.add(scope)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Scope', scope.id, request_data)

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
            scope = Scope.query.filter_by(id=id).first()
            if scope:
                scope_obj = self.scope_schema.dump(scope)
                db.session.delete(scope)
                db.session.commit()
                return self.response_handler.successful_delete_response('Scope', id, scope_obj)
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
        scope = Scope.query.filter_by(id=id).first()
        if not scope:
            return self.response_handler.not_found_response(id)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        errors = self.scope_schema.validate(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(scope, k):
                setattr(scope, k, v)
        try:
            db.session.commit()
            return self.response_handler.successful_update_response('Scope', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)


scope_bp = Blueprint('scope_ep', __name__)
scope_api = Api(scope_bp)
scope_api.add_resource(ScopeResource, '/scopes', '/scopes/<string:id>')
