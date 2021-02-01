import json
import requests
from flask import Blueprint, render_template, request, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, validators

from authserver.db import db, User, OAuth2Client

home_bp = Blueprint('home_ep', __name__, static_folder='static',
                    template_folder='templates', url_prefix='/')


class LoginForm(Form):
    username = StringField(
        'Username', [validators.DataRequired(), validators.length(min=4, max=40)])
    password = PasswordField('Password', [validators.DataRequired()])


class RecoverPasswordForm(Form):
    username = StringField(
        'Username', [validators.DataRequired(), validators.length(min=4, max=40)])


@home_bp.route('/', methods=['GET', 'POST'])
def login():
    errors = None
    form = LoginForm(request.form)
    client_id = request.args.get('client_id')
    return_to = request.args.get('return_to')

    if request.method == 'GET':
        if not client_id or not return_to:
            return render_template('login.html', form=form)
        else:
            return render_template('login.html', client_id=client_id, return_to=return_to, form=form)

    if form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        error_msg = "You did not enter valid login credentials."

        try:
            if (not user.active) or (not user.can_login) or (not user.verify_password(password)):
                errors = error_msg
            else:
                session['id'] = user.id
                return redirect(return_to)
        except AttributeError:
            errors = error_msg

        return render_template('login.html', client_id=client_id, return_to=return_to, form=form, errors=errors)


@home_bp.route('/recover', methods=['GET', 'POST'])
def recover_password():
    errors = None
    form = RecoverPasswordForm(request.form)
    if request.method == 'GET':
        return render_template('recover.html', form=form)
    else:
        return render_template('recover.html', form=form, errors=errors)
