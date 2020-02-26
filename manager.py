import os
from flask_script import Manager
from flask_migrate import MigrateCommand
from authserver import create_app

environment = os.getenv('APP_ENV', None)
app = application = create_app(environment)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
