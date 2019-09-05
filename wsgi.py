import os
from authserver import create_app
environment = os.getenv('APP_ENV', None)

app = application = create_app(environment)
