##########################################
#
# About
#
##########################################


import os
from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import UserMixin, LoginManager, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

##########################################
# init:
##########################################

password = 'thesecret'
basedir = os.path.abspath(os.path.dirname(__file__))


class Base(DeclarativeBase):
      pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db/main.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


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


with app.app_context():
    db.create_all()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(64))

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
        return user

    def __repr__(self):
        return '<User {0}>'.format(self.name)


##########################################
# routes:
##########################################


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if current_user.is_authenticated:
            names = db.session.execute(db.select(TNVDName).order_by(TNVDName.id)).scalars()
            print(*names)
            return render_template('home.html', current_user=current_user)
        else:
            return redirect(url_for('login'))

    # if request.method == 'GET':
    #     names = db.session.execute(db.select(TNVDName).order_by(TNVDName.id)).scalars()
    #     print(*names)
    #     return render_template('home.html', current_user=current_user)
    # else:
    #     read_xlsx_file()
    #     return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        else:
            return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # Логика выхода из системы
    return redirect(url_for('login'))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return render_template('edit.html')
        else:
            save_xlsx_file()
            return redirect(url_for('edit'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


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


@login_manager.user_loader
def load_user(user_id):
    return None


# @login_manager.request_loader
# def load_user_from_request(request):
#     return None


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
