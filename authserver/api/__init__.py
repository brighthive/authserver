from authserver.api.health import health_api_bp
from authserver.api.data_trust import data_trust_bp
from authserver.api.user import user_bp
from authserver.api.client import client_bp
from authserver.api.client_secret import delete_client_secret_bp, rotate_client_secret_bp
from authserver.api.oauth2 import oauth2_bp
from authserver.api.role import role_bp