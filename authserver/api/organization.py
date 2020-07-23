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
            organizations_obj = self.organizations_schema.dump(organizations).data
            return self.response_handler.get_all_response(organizations_obj)
        else:
            organization = Organization.query.filter_by(id=id).first()
            if organization:
                organization_obj = self.organization_schema.dump(organization).data
                return self.response_handler.get_one_response(organization_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    @require_oauth()
    def post(self):
        # Check for data, since all POST requests need it.
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        if not request_data:
            return self.response_handler.empty_request_body_response()

        data, errors = self.organization_schema.load(request_data)
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

    # Put
    # Patch
    # Delete


organization_bp = Blueprint('organization_ep', __name__)
organization_api = Api(organization_bp)
organization_api.add_resource(OrganizationResource, '/organizations', '/organizations/<string:id>')