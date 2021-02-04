import string
import random
from datetime import datetime
from flask import Blueprint, render_template, request, abort
from wtforms import Form, StringField, PasswordField, validators
from authserver.db import db, User, PasswordRecovery
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
    password = PasswordField('Enter your new password', [validators.DataRequired(), validators.length(min=9)])
    confirm_password = PasswordField('Re-type your new password', [validators.DataRequired(), validators.length(min=9)])


@password_recovery_bp.route('/password-recovery', methods=['GET', 'POST'])
def recover_password(config: AbstractConfiguration, graph_db: AbstractGraphDatabase, mailer: AbstractMailService):
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
                    status = mailer.send_password_recovery_email(to=person['email'], firstname=person['givenName'], username=user.username, recovery_url=recovery_url)
                    if status:
                        password_recovery = PasswordRecovery(nonce, user.id)
                        db.session.add(password_recovery)
                        db.session.commit()
                except Exception as e:
                    db.session.rollback()
        # NOTE: for security purposes, we still render the success email whether or not the user was found.
        return render_template('success.html', default_app_url=config.default_app_url, heading='Email Sent!', body='A password reset email has been sent to the email address associated with the entered username.')


@password_recovery_bp.route('/password-reset', methods=['GET', 'POST'])
def reset_password(config: AbstractConfiguration, graph_db: AbstractGraphDatabase, mailer: AbstractMailService):
    errors = None
    nonce = request.args.get('n', None)
    if not nonce:
        abort(404)

    password_recovery = PasswordRecovery.query.filter_by(nonce=nonce).first()
    if (not password_recovery or password_recovery.is_expired or password_recovery.date_recovered is not None):
        abort(404)

    form = ResetPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('reset.html', form=form)
    else:
        password = form.password.data
        confirm_password = form.confirm_password.data
        if form.validate():
            if password != confirm_password:
                return render_template('reset.html', form=form, errors='Password fields must match.')
            user = User.query.filter_by(id=password_recovery.user_id).first()
            if user:
                try:
                    user.password = password
                    user.date_last_updated = datetime.utcnow()
                    password_recovery.date_recovered = datetime.utcnow()
                    db.session.commit()

                    person_query = f"MATCH (p:Person{{id:'{user.person_id}'}}) RETURN p"
                    try:
                        person = graph_db.query(person_query).single()[0]
                        mailer.send_password_reset_email(to=person['email'], firstname=person['givenName'])
                    except Exception as e:
                        pass

                    return render_template('success.html', default_app_url=config.default_app_url, heading='Update Successful!', body='Please log in with your new credentials.')
                except Exception:
                    db.session.rollback()
                    abort(404)
        else:
            return render_template('reset.html', form=form, errors='Password must be a minimum of 9 characters long.')
