import json
from datetime import datetime

from flask import Blueprint
from flask_restful import Api, Resource, request

from authserver.db import db, Organization, OrganizationSchema
from authserver.utilities import ResponseBody, require_oauth


class OrganizationResource(Resource):
    """An Organization Resource.

    This resource defines an Organization, which may have one or more associated Users.
    """

    def __init__(self):
        self.organization_schema = OrganizationSchema()
        self.organizations_schema = OrganizationSchema(many=True)
        self.response_handler = ResponseBody()

    @require_oauth()
    def get(self, id: str = None):
        if not id:
            organizations = Organization.query.all()
            organizations_obj = self.organizations_schema.dump(organizations)
            return self.response_handler.get_all_response(organizations_obj)
        else:
            organization = Organization.query.filter_by(id=id).first()
            if organization:
                organization_obj = self.organization_schema.dump(organization)
                return self.response_handler.get_one_response(organization_obj, request={'id': id})
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

        errors = self.organization_schema.validate(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        try:
            organization = Organization(name=request_data['name'])
            db.session.add(organization)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Organization', organization.id, request_data)

    @require_oauth()
    def delete(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()
        try:
            organization = Organization.query.filter_by(id=id).first()
            if organization:
                organization_obj = self.organization_schema.dump(organization)
                db.session.delete(organization)
                db.session.commit()
                return self.response_handler.successful_delete_response('Organization', id, organization_obj)
            else:
                return self.response_handler.not_found_response(id)
        except Exception:
            return self.response_handler.not_found_response(id)

    @require_oauth()
    def put(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self._update(request, id, False)

    @require_oauth()
    def patch(self, id: str = None):
        if id is None:
            return self.response_handler.method_not_allowed_response()

        return self._update(request, id)

    def _update(self, request, id: str, partial=True):
        """General update function for PUT and PATCH.

        Using Marshmallow, the logic for PUT and PATCH differ by a single parameter. This method abstracts that logic
        and allows for switching the Marshmallow validation to partial for PATCH and complete for PUT.
        """
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()

        if not request_data:
            return self.response_handler.empty_request_body_response()

        organization = Organization.query.filter_by(id=id).first()
        if not organization:
            return self.response_handler.not_found_response(id)

        errors = self.organization_schema.validate(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(organization, k):
                setattr(organization, k, v)
        try:
            organization.date_last_updated = datetime.utcnow()
            db.session.commit()
            return self.response_handler.successful_update_response('Organization', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)


organization_bp = Blueprint('organization_ep', __name__)
organization_api = Api(organization_bp)
organization_api.add_resource(OrganizationResource, '/organizations', '/organizations/<string:id>')
