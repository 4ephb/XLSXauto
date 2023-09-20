from flask import Flask, render_template, redirect, request
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == 'GET':
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
def edit():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    return "Nothing here.."


def read_xlsx_file():
    print("reading xlsx..")


def save_xlsx_file():
    print("reading xlsx..")
