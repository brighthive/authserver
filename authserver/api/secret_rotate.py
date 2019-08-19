import json
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authserver.utilities import ResponseBody


class SecretRotateResource(Resource):
    """Secret Rotate Resource

    This resource provides a POST function for rotating a client secret.

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
        
        client.client_secret = gen_salt(48)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_update_response('Client', client_id)

secret_rotate_bp = Blueprint('secret_rotate_ep', __name__)
secret_rotate_api = Api(secret_rotate_bp)
secret_rotate_api.add_resource(SecretRotateResource, '/clients/secret-rotate')