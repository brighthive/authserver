from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, To, Content, Mail, template_id
from abc import ABC, abstractmethod
from injector import inject
from authserver.config import AbstractConfiguration


class AbstractMailService(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def send_password_recovery_email(self, to: str, firstname: str, username: str, reset_url: str):
        pass

    @abstractmethod
    def send_password_reset_email(self, to: str, firstname: str, username: str):
        pass


class SendGridMailService(AbstractMailService):
    @inject
    def __init__(self, config: AbstractConfiguration):
        super().__init__()
        self.config = config
        self.sg_client = SendGridAPIClient(api_key=self.config.sendgrid_api_key)

    def send_password_recovery_email(self, to: str, firstname: str, username: str, recovery_url: str):
        from_email = Email(self.config.sendgrid_from_email)
        to_email = To(to)
        mail = Mail(from_email, to_email)
        mail.template_id = self.config.sendgrid_recovery_template_id
        mail.dynamic_template_data = {
            'firstname': firstname,
            'username': username,
            'recovery_url': recovery_url
        }
        response = self.sg_client.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    def send_password_reset_email(self, to: str, firstname: str, username: str):
        pass
