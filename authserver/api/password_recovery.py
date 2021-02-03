import json
import requests
import string
import random
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from wtforms import Form, StringField, PasswordField, validators

from authserver.config import AbstractConfiguration

# TODO: Move into code after testing
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail, template_id

from authserver.db import db, User, OAuth2Client

password_recovery_bp = Blueprint('password_recovery_ep', __name__, static_folder='static',
                                 template_folder='templates', url_prefix='/')


def string_num_generator(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))


class RecoverPasswordForm(Form):
    username = StringField(
        'Username', [validators.DataRequired(), validators.length(min=4, max=40)])


class ResetPasswordForm(Form):
    password = PasswordField('Enter your new password', [validators.DataRequired()])
    confirm_password = PasswordField('Re-type your new password', [validators.DataRequired()])


@password_recovery_bp.route('/password-recovery', methods=['GET', 'POST'])
def recover_password(config: AbstractConfiguration):
    errors = None
    form = RecoverPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('recover.html', form=form)
    else:
        sg = sendgrid.SendGridAPIClient(api_key='foo')
        from_email = Email('foo')
        to_emails = [To('foo')]
        template_id = 'foo'
        mail = Mail(from_email, to_emails)
        mail.template_id = template_id
        # response = sg.client.mail.send.post(request_body=mail.get())
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        print(request.url_root + 'reset-password?q=' + string_num_generator(30))
        return render_template('success.html', default_app_url=config.default_app_url, heading='Email Sent!', body='A password reset email has been sent to the email address associated with the entered username.')


@password_recovery_bp.route('/password-reset', methods=['GET', 'POST'])
def reset_password(config: AbstractConfiguration):
    errors = None
    form = ResetPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('reset.html', form=form)
    else:
        # sg = sendgrid.SendGridAPIClient(api_key='foo')
        # from_email = Email('foo')
        # to_emails = [To('foo')]
        # template_id = 'foo'
        # mail = Mail(from_email, to_emails)
        # mail.template_id = template_id
        # # response = sg.client.mail.send.post(request_body=mail.get())
        # # print(response.status_code)
        # # print(response.body)
        # # print(response.headers)
        # print(request.url_root + 'reset-password?q=' + string_num_generator(30))
        return render_template('success.html', default_app_url=config.default_app_url, heading='Update Successful!', body='Please log in with your new credentials.')
