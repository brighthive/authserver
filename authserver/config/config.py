"""Application Configuration

This module contains a general-purpose configuration class, subclasses for
different application environments, and a factory for creating configuration
objects based on the determined environment.

"""

import os
import json
from datetime import datetime
from abc import ABC
import logging

class ConfigurationEnvironmentNotFoundError(Exception):
    pass


class AbstractConfiguration(ABC):
    """Base configuration class.

    This is the base configuration class. It should be extended by other configuration classes on a per
    environment basis.

    Class Attributes:
        RELATIVE_PATH (str): The relative path of the current file.
        ABSOLUTE_PATH (str): The absolute path of the current file.
        ROOT_PATH (str): The root path of the application (subtracting the relative path from the absolute path).
        SETTINGS_FILE (obj): The path of the settings file that contains information about the API.

    """
    RELATIVE_PATH = os.path.dirname(os.path.relpath(__file__))
    ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    ROOT_PATH = ABSOLUTE_PATH.split(RELATIVE_PATH)[0]
    SETTINGS_FILE = os.path.join(ABSOLUTE_PATH, 'settings.json')

    def __init__(self):
        self.configuration_name = 'BASE'
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

        self.postgres_user = os.getenv('PG_USER', 'brighthive_admin')
        self.postgres_password = os.getenv('PG_PASSWORD', 'password')
        self.postgres_hostname = os.getenv('PG_HOSTNAME', 'localhost')
        self.postgres_database = os.getenv('PG_DB', 'authserver')
        self.postgres_port = os.getenv('PG_PORT', 5432)
        self.sqlalchemy_database_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.postgres_user,
            self.postgres_password,
            self.postgres_hostname,
            self.postgres_port,
            self.postgres_database
        )

        self.graph_db_user = os.getenv('GRAPH_DB_USER', 'neo4j')
        self.graph_db_password = os.getenv('GRAPH_DB_PASSWORD', 'passw0rd')
        self.graph_db_hostname = os.getenv('GRAPH_DB_HOSTNAME', 'localhost')
        self.graph_db_port = os.getenv('GRAPH_DB_PORT', '7687')
        self.graph_db_encrypted = os.getenv('GRAPH_DB_ENCRYPTED', 'false').upper() == 'TRUE'
        self.neo4j_production = os.getenv("NEO4J_PRODUCTION", "False").upper() == 'TRUE'

        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', 'apikey')
        self.sendgrid_from_email = os.getenv('SENDGRID_FROM_EMAIL', 'user@example.com')
        self.sendgrid_recovery_template_id = os.getenv('SENDGRID_RECOVERY_TEMPLATE_ID', 'recovery-id')
        self.sendgrid_reset_template_id = os.getenv('SENDGRID_RESET_TEMPLATE_ID', 'recovery-id')
        self.default_app_url = os.getenv('DEFAULT_APP_URL', 'http://localhost:8001')

        self.permission_service_url = os.getenv('BH_PERMISSIONS_SERVICE_URI', 'https://rixvnfq6r0.execute-api.us-west-2.amazonaws.com/devtest')
        signature_private_path = os.getenv('SIGNATURE_PRIVATE_PATH', None)

        if signature_private_path is None:
            logging.warn("Private key for JWT signature not defined.")
        
        try:
            with open(signature_private_path, "rb") as key_file:
                self.signature_key = key_file.read()
        except (FileNotFoundError, TypeError) as e:
            logging.exception("Failed to find or open JWT private key.")


    @staticmethod
    def get_app_status():
        """Retrieves information about the API for health check.

        """
        try:
            with open(AbstractConfiguration.SETTINGS_FILE, 'r') as fh:
                settings = json.load(fh)
        except Exception:
            settings = {}

        settings['api_status'] = 'OK'
        settings['timestamp'] = str(datetime.utcnow())
        return settings

    @property
    def graph_db_connection_uri(self):
        if self.neo4j_production:
            return f'neo4j+s://{self.graph_db_hostname}'
        return f'bolt://{self.graph_db_hostname}:{self.graph_db_port}'


class DevelopmentConfiguration(AbstractConfiguration):
    """Development environment configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ENV = 'development'
    DEBUG = True
    TESTING = False

    def __init__(self):
        super().__init__()
        self.configuration_name = 'DEVELOPMENT'


class TestingConfiguration(AbstractConfiguration):
    """Testing environment configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ENV = 'testing'
    DEBUG = False
    TESTING = True

    def __init__(self):
        super().__init__()
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.configuration_name = 'TESTING'
        self.postgres_user = 'test_user'
        self.postgres_password = 'test_password'
        self.postgres_hostname = 'localhost'
        self.container_name = 'postgres-test'
        self.image_name = 'postgres'
        self.image_version = '11.1'
        self.postgres_database = 'authservice_test'
        self.postgres_port = 5433
        self.sqlalchemy_database_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.postgres_user,
            self.postgres_password,
            self.postgres_hostname,
            self.postgres_port,
            self.postgres_database
        )

    def get_postgresql_image(self):
        return '{}:{}'.format(self.image_name, self.image_version)


class JenkinsConfiguration(AbstractConfiguration):
    """Testing environment configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ENV = 'testing'
    DEBUG = False
    TESTING = True

    def __init__(self):
        super().__init__()
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
        self.configuration_name = 'TESTING'
        self.postgres_user = 'test_user'
        self.postgres_password = 'test_password'
        self.postgres_hostname = os.getenv('DB_PORT_5432_TCP_ADDR', '0.0.0.0')
        self.container_name = 'postgres-test'
        self.image_name = 'postgres'
        self.image_version = '11.1'
        self.postgres_database = 'authservice_test'
        self.postgres_port = os.getenv('DB_PORT_5432_TCP_PORT', 5432)
        self.sqlalchemy_database_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.postgres_user,
            self.postgres_password,
            self.postgres_hostname,
            self.postgres_port,
            self.postgres_database
        )


class StagingConfiguration(AbstractConfiguration):
    """Staging environment configuration."""

    def __init__(self):
        super().__init__()
        self.configuration_name = 'STAGING'


class SandboxConfiguration(AbstractConfiguration):
    """Sandbox environment configuration."""

    def __init__(self):
        super().__init__()
        self.configuration_name = 'SANDBOX'


class ProductionConfiguration(AbstractConfiguration):
    """Production environment configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'production'
    DEBUG = False
    TESTING = False

    def __init__(self):
        super().__init__()
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '0'
        self.configuration_name = 'PRODUCTION'
        self.postgres_user = os.getenv('PG_USER')
        self.postgres_password = os.getenv('PG_PASSWORD')
        self.postgres_hostname = os.getenv('PG_HOSTNAME')
        self.postgres_database = os.getenv('PG_DB')
        self.postgres_port = os.getenv('PG_PORT', 5432)
        self.sqlalchemy_database_uri = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.postgres_user,
            self.postgres_password,
            self.postgres_hostname,
            self.postgres_port,
            self.postgres_database
        )

        self.graph_db_user = os.getenv('GRAPH_DB_USER')
        self.graph_db_password = os.getenv('GRAPH_DB_PASSWORD')
        self.graph_db_hostname = os.getenv('GRAPH_DB_HOSTNAME')
        self.graph_db_port = os.getenv('GRAPH_DB_PORT')
        self.graph_db_encrypted = os.getenv('GRAPH_DB_ENCRYPTED', 'false').upper() == 'TRUE'

        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.sendgrid_from_email = os.getenv('SENDGRID_FROM_EMAIL')
        self.sendgrid_recovery_template_id = os.getenv('SENDGRID_RECOVERY_TEMPLATE_ID')

        self.default_app_url = os.getenv('DEFAULT_APP_URL')


class ConfigurationFactory(object):
    """Application configuration factory."""

    @staticmethod
    def from_env():
        environment = os.getenv('APP_ENV', 'DEVELOPMENT').upper()
        return ConfigurationFactory.get_config(environment)

    @staticmethod
    def get_config(environment: str):
        """Retrieves a configuration object based on its environment type.

        Args:
            environment (str): The name of the environment to return configuration object for.
                May be: DEVELOPMENT, TESTING, STAGING, SANDBOX, PRODUCTION

        Returns:
            obj: A configuration object that encapsulates the settings for the specified environment.

        Raises:
            ConfigurationEnvironmentNotFoundError: If an unknown configuration type is passed.

        """
        if environment is None:
            environment = 'DEVELOPMENT'
        else:
            environment = environment.upper()
        if environment == 'DEVELOPMENT':
            return DevelopmentConfiguration()
        elif environment == 'TESTING':
            is_jenkins = bool(int(os.getenv('IS_JENKINS_TEST', '0')))
            if is_jenkins:
                return JenkinsConfiguration()
            else:
                return TestingConfiguration()
        elif environment == 'STAGING':
            return StagingConfiguration()
        elif environment == 'SANDBOX':
            return SandboxConfiguration()
        elif environment == 'PRODUCTION':
            return ProductionConfiguration()
        else:
            raise ConfigurationEnvironmentNotFoundError(
                'Cannot find configuration of type {}'.format(environment))

    @staticmethod
    def generate_secret_key():
        """Generate a secret for securing the Flask session.
        Returns:
            byte: A random string of bytes for secret.
        """
        environment = os.getenv('APP_ENV', 'development')
        if environment.lower() == 'production':
            return os.getenv('SECRET_KEY', os.urandom(16))
        else:
            return b'supersecretaccesscode'
