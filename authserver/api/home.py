import json
import requests
from flask import Blueprint, render_template, request, redirect, url_for, session
from wtforms import Form, StringField, PasswordField, validators

from authserver.db import db, User, OAuth2Client

home_bp = Blueprint('home_ep', __name__, static_folder='static', template_folder='templates', url_prefix='/')


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired(), validators.length(min=4, max=40)])
    password = PasswordField('Password', [validators.DataRequired()])


@home_bp.route('/', methods=['GET', 'POST'])
def login():
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
        if user and user.verify_password(password):
            session['id'] = user.id
            return redirect(return_to)
        else:
            if not client_id or not return_to:
                return redirect(url_for('home_ep.login'))
            else:
                return redirect(url_for('home_ep.login', client_id=client_id, return_to=return_to))
