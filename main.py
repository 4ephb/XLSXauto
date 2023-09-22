##########################################
#
# About
#
##########################################


import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import forms
from utils import secret_key


##########################################
# init:
##########################################


password = 'thesecret'


class Base(DeclarativeBase):
    pass


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
DEBUG = True
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db/main.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(model_class=Base)
db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()

# initialize extensions
bootstrap.init_app(app)
db.init_app(app)
login_manager.init_app(app)
secret_key(app)

login_manager.login_view = 'login'

##########################################
# models:
##########################################


class TNVDName(db.Model):
    __tablename__ = 'tnvd_names'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    tnvd: Mapped[str] = mapped_column(String, nullable=False)
    low: Mapped[str] = mapped_column(Float)
    high: Mapped[str] = mapped_column(Float)


class TNVDDescription(db.Model):
    __tablename__ = 'tnvd_description'
    # number: Mapped[int] = mapped_column(Integer, nullable=False)
    # description: Mapped[str] = mapped_column(String, nullable=False)
    number = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String, nullable=False)


class BrandCategories(db.Model):
    __tablename__ = 'brand_categories'
    # cheapest: Mapped[str] = mapped_column(String)
    # premium: Mapped[str] = mapped_column(String)
    cheapest = db.Column(db.String, primary_key=True)
    premium = db.Column(db.String)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(name, password):
        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # return user

    def __repr__(self):
        return '<User {0}>'.format(self.name)


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##########################################
# routes:
##########################################


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        names = db.session.execute(db.select(TNVDName).order_by(TNVDName.id)).scalars()
        print(*names)
        username = session.get('username')
        return render_template('home.html', current_user=current_user)
    else:
        read_xlsx_file()
        return redirect(url_for('login'))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        return render_template('edit.html')
    else:
        save_xlsx_file()
        return redirect(url_for('edit'))


@app.route('/reg', methods=['GET'])
def reg():
    if request.method == 'GET':
        if User.query.filter_by(name='oleg').first() is None:
            User.register('oleg', '1234')
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # name = request.form.get('name')
    # password = request.form.get('password')
    # if name and password:
    #     user = User.query.filter_by(name=name).first()
    #     if user and check_password_hash(user.password, password):
    #         login_user(user)
    #         next_page = request.args.get('next')
    #         return redirect(next_page)
    #     else:
    #         print('Логин или пароль не верны')
    #         flash('Логин или пароль не верны')
    # else:
    #     print('Пожалуйста, заполните поля логин и пароль')
    #     flash('Пожалуйста, заполните поля логин и пароль')
    #
    # return render_template('login.html')

    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user is None or not user.verify_password(form.password.data):
            return redirect(url_for('login', **request.args))
        login_user(user, form.remember_me.data)
        session['name'] = request.form['name']
        return redirect(request.args.get('next') or url_for('home'))
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill all fields!')
        elif password != password2:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login') + '?next=' + request.url)
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


@app.errorhandler(401)
def page_not_found(error):
    return render_template("401.html")


@app.errorhandler(500)
def page_not_found(error):
    return render_template("500.html")


##########################################
# logic:
##########################################


def read_xlsx_file():
    print('reading xlsx..')


def save_xlsx_file():
    print('saving xlsx..')
