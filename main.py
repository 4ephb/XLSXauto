##########################################
#
# About
#
##########################################


import os
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float


##########################################
# init:
##########################################


basedir = os.path.abspath(os.path.dirname(__file__))

class Base(DeclarativeBase):
      pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db/main.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


##########################################
# models:
##########################################


class TNVDName(db.Model):
    __tablename__ = "tnvd_names"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    tnvd: Mapped[str] = mapped_column(String, nullable=False)
    low: Mapped[str] = mapped_column(Float)
    high: Mapped[str] = mapped_column(Float)

with app.app_context():
    db.create_all()


##########################################
# routes:
##########################################


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'GET':
        names = db.session.execute(db.select(TNVDName).order_by(TNVDName.id)).scalars()
        print(*names)

        return render_template("home.html")
    else:
        read_xlsx_file()
        return redirect(url_for('edit'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == 'GET':
        return render_template("edit.html")
    else:
        save_xlsx_file()
        return redirect(url_for('edit'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    return "Nothing here.."


##########################################
# logic:
##########################################


def read_xlsx_file():
    print("reading xlsx..")


def save_xlsx_file():
    print("reading xlsx..")
