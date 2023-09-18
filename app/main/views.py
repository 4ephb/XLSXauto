from flask import render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user
from ..models import User, Glyph, Tone, Kin
from . import main
from .forms import LoginForm
from sqlalchemy import asc

import datetime


@main.route('/')
def home():
    return render_template('site/home.html')


@main.route('/admin')
def admin():
    return redirect(url_for('glyph.list'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('main.login', **request.args))
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('glyph.list'))
    return render_template('site/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@main.errorhandler(404)
def not_found(e):
    return 'Nothing here..'


##########################################
# Logic:
##########################################
