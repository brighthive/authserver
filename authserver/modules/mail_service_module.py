from injector import singleton, Module
from authserver.utilities.mail_service import AbstractMailService, SendGridMailService


class MailServiceModule(Module):
    def configure(self, binder):
        binder.bind(AbstractMailService, to=SendGridMailService, scope=singleton)
