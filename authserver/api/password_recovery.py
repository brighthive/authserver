import string
import random
from flask import Blueprint, render_template, request, abort
from wtforms import Form, StringField, PasswordField, validators
from authserver.db import User
from authserver.config import AbstractConfiguration
from authserver.db.graph_database import AbstractGraphDatabase
from authserver.utilities.mail_service import AbstractMailService

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
def recover_password(config: AbstractConfiguration, graph_db: AbstractGraphDatabase, mailer: AbstractMailService):
    errors = None
    form = RecoverPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('recover.html', form=form)
    else:
        if form.validate():
            username = form.username.data
            user = User.query.filter_by(username=username).first()
            if user:
                person_id = user.person_id
                person_query = f"MATCH (p:Person{{id:'{person_id}'}}) RETURN p"
                try:
                    person = graph_db.query(person_query).single()[0]
                    nonce = string_num_generator(30)
                    recovery_url = f'{request.url_root}password-reset?n={nonce}'
                    mailer.send_password_recovery_email(to=person['email'], firstname=person['givenName'], username=user.username, recovery_url=recovery_url)
                except Exception:
                    pass
        # NOTE: for security purposes, we still render the success email whether or not the user was found.
        return render_template('success.html', default_app_url=config.default_app_url, heading='Email Sent!', body='A password reset email has been sent to the email address associated with the entered username.')


@password_recovery_bp.route('/password-reset', methods=['GET', 'POST'])
def reset_password(config: AbstractConfiguration):
    errors = None
    nonce = request.args.get('n', None)
    if not nonce:
        abort(404)
    form = ResetPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('reset.html', form=form)
    else:
        return render_template('success.html', default_app_url=config.default_app_url, heading='Update Successful!', body='Please log in with your new credentials.')
