import json

from flask import Blueprint
from flask_restful import Api, Resource, request
from werkzeug.security import gen_salt

from authserver.db import OAuth2Client, db
from authserver.utilities import ResponseBody


class ClientSecret(Resource):
    """Client Secret Resource

    This resource provides a general POST function for updating the `client_secret` of a Client:
    namely, deleting a secret (i.e., disabling a client) or rotating a secret.

    """

    def __init__(self, secret_value):
        self.response_handler = ResponseBody()
        self.secret_value = secret_value
    
    def post(self):
        try:
            request_data = request.get_json(force=True)
        except Exception as e:
            return self.response_handler.empty_request_body_response()
        
        try:
            client_id = request_data['id']
        except KeyError as e:
            return self.response_handler.custom_response(code=422, messages='Please provide the ID of the client.')
        
        client = OAuth2Client.query.filter_by(id=client_id).first()
        if not client:
            return self.response_handler.not_found_response(client_id)
        
        client.client_secret = self.secret_value

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_update_response('Client', client_id)


class DeleteClientSecret(ClientSecret):
    def __init__(self):
        super().__init__(secret_value=None)

class RotateClientSecret(ClientSecret):
    def __init__(self):
        new_secret = gen_salt(48)
        super().__init__(secret_value=new_secret)

delete_client_secret_bp = Blueprint('delete_client_secret_ep', __name__)
delete_client_secret_api = Api(delete_client_secret_bp)
delete_client_secret_api.add_resource(DeleteClientSecret, '/clients/secret-delete')

rotate_client_secret_bp = Blueprint('rotate_client_secret_ep', __name__)
rotate_client_secret_api = Api(rotate_client_secret_bp)
rotate_client_secret_api.add_resource(RotateClientSecret, '/clients/secret-rotate')