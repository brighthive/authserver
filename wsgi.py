import os
from authserver import create_app

from werkzeug.middleware.proxy_fix import ProxyFix

environment = os.getenv('APP_ENV', None)

app = application = create_app(environment)

if environment == 'PRODUCTION':
    app = ProxyFix(app)
