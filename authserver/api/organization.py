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
    
    # @require_oauth()
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

organization_bp = Blueprint('organization_ep', __name__)
organization_api = Api(organization_bp)
organization_api.add_resource(OrganizationResource, '/organizations', '/organizations/<string:id>')