"""Data Trust API

A simple API for returning health check information to clients.

"""

from flask import Blueprint
from flask_restful import Resource, Api, request
from authserver.db import db, DataTrust, DataTrustSchema
from authserver.utilities import ResponseBody
from datetime import datetime


class DataTrustResource(Resource):
    """A Data Trust Resource."""

    def __init__(self):
        self.data_trust_schema = DataTrustSchema()
        self.data_trusts_schema = DataTrustSchema(many=True)
        self.response_handler = ResponseBody()

    def get(self, id: str = None):
        if not id:
            data_trusts = DataTrust.query.all()
            data_trusts_obj = self.data_trusts_schema.dump(data_trusts).data
            return self.response_handler.get_all_response(data_trusts_obj)
        else:
            data_trust = DataTrust.query.filter_by(id=id).first()
            if data_trust:
                data_trusts_obj = self.data_trust_schema.dump(data_trust).data
                return self.response_handler.get_one_response(data_trusts_obj, request={'id': id})
            else:
                return self.response_handler.not_found_response(id)

    def post(self, id=None):
        if id is not None:
            return self.response_handler.method_not_allowed_response()
        request_data = request.get_json(force=True)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        data, errors = self.data_trust_schema.load(request_data)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)
        try:
            data_trust = DataTrust(request_data['data_trust_name'])
            db.session.add(data_trust)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)
        return self.response_handler.successful_creation_response('Data Trust', data_trust.id, request_data)

    def patch(self, id: str):
        return self.update(id)

    def put(self, id: str):
        return self.update(id, False)

    def delete(self, id: str):
        try:
            data_trust = DataTrust.query.filter_by(id=id).first()
            if data_trust:
                data_trust_obj = self.data_trust_schema.dump(data_trust).data
                db.session.delete(data_trust)
                db.session.commit()
                return self.response_handler.successful_delete_response('Data Trust', id, data_trust_obj)
            else:
                return self.response_handler.not_found_response(id)
        except Exception:
            return self.response_handler.not_found_response(id)

    def update(self, id: str, partial=True):
        """General update function for PUT and PATCH.

        Using Marshmallow, the logic for PUT and PATCH differ by a single parameter. This method abstracts that logic
        and allows for switching the Marshmallow validation to partial for PATCH and complete for PUT.

        """
        request_data = request.get_json(force=True)
        data_trust = DataTrust.query.filter_by(id=id).first()
        if not data_trust:
            return self.response_handler.not_found_response(id)
        if not request_data:
            return self.response_handler.empty_request_body_response()
        data, errors = self.data_trust_schema.load(request_data, partial=partial)
        if errors:
            return self.response_handler.custom_response(code=422, messages=errors)

        for k, v in request_data.items():
            if hasattr(data_trust, k):
                setattr(data_trust, k, v)
        try:
            data_trust.date_last_updated = datetime.utcnow()
            db.session.commit()
            return self.response_handler.successful_update_response('Data Trust', id, request_data)
        except Exception as e:
            db.session.rollback()
            exception_name = type(e).__name__
            return self.response_handler.exception_response(exception_name, request=request_data)


data_trust_bp = Blueprint('data_trust_ep', __name__)
data_trust_api = Api(data_trust_bp)
data_trust_api.add_resource(DataTrustResource, '/datatrusts', '/datatrusts/<string:id>')
