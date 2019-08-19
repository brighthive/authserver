"""Client API

An API for registering clients with Auth Server.

"""

# import json
# from uuid import uuid4
# from datetime import datetime
# from flask import Blueprint
# from flask_restful import Resource, Api, request
# from werkzeug.security import gen_salt
# from authserver.db import db, DataTrust, DataTrustSchema, User, UserSchema, OAuth2Client,\
#     OAuth2ClientSchema, Role
# from authserver.utilities import ResponseBody


# class ClientResource(Resource):
#     """Client Resource

#     This resource represents an OAuth 2.0 client that is associated with a user.

#     """

#     def __init__(self):
#         self.client_schema = OAuth2ClientSchema()
#         self.clients_schema = OAuth2ClientSchema(many=True)
#         self.response_handler = ResponseBody()