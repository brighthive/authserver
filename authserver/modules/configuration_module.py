from injector import singleton, Module
from authserver.config import AbstractConfiguration, ConfigurationFactory


class ConfigurationModule(Module):
    def configure(self, binder):
        binder.bind(AbstractConfiguration, to=ConfigurationFactory.from_env(), scope=singleton)
