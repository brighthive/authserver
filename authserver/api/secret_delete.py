"""Client API

An API for registering clients with Auth Server.

"""

import json
from uuid import uuid4
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.db import db, OAuth2Client
from authserver.utilities import ResponseBody


class SecretDeleteResource(Resource):
    """Secret Delete Resource

    This resource provides a POST function for deleting a secret, i.e., disabling a client.

    """

    def __init__(self):
        self.response_handler = ResponseBody()
    
    def post(self):
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        
        try:
            client_id = request_data['client_id']
        except KeyError as e:
            return self.response_handler.custom_response(code=422, messages='Please provide the client_id.')
        
        client = OAuth2Client.query.filter_by(id=client_id).first()
        if not client:
            return self.response_handler.not_found_response(client_id)
        
        client.client_secret = None

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_update_response('Client', client_id)

secret_delete_bp = Blueprint('secret_delete_ep', __name__)
secret_delete_api = Api(secret_delete_bp)
secret_delete_api.add_resource(SecretDeleteResource, '/clients/secret-delete')