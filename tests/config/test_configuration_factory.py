"""Unit tests for application configuration."""

from expects import expect, equal, raise_error
from authserver.config import ConfigurationFactory, ConfigurationEnvironmentNotFoundError


class TestApplicationConfigurationFactory():
    def test_configuration_factory(self, environments):
        for environment in environments:
            env = ConfigurationFactory.get_config(environment)
            expect(env.configuration_name).to(equal(environment))
        expect(lambda: ConfigurationFactory.get_config('InvalidEnvironment')).to(raise_error(ConfigurationEnvironmentNotFoundError))
