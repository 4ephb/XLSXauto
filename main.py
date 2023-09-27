##########################################
#
# About
#
##########################################

import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
import pandas as pd
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import forms
# from flask_wtf import FlaskForm
from utils import secret_key
import openpyxl
from flask_cors import CORS, cross_origin
# import json

##########################################
# init:
##########################################

basedir = os.path.abspath(os.path.dirname(__file__))

# Имена колонок Result таблицы
result_columns = [
    'НАИМЕНОВАНИЕ1', 'НАИМЕНОВАНИЕ2', 'ИЗГОТОВИТЕЛЬ', 'ТМ', 'МАРКА', 'МОДЕЛЬ',
    'АРТ', 'СПТ', 'КОЛ-ВО', 'КОД', 'НАИМ', 'КОД ТНВД', 'ДОП КОД', 'ВЕС ШТ',
    'БР', 'НТ', '$/КГ', 'ЦЕНА', 'МЕСТА', 'МЕСТ ЧАСТ', 'ЕСТЬ/НЕТ', 'КОД УП',
    'ДОП КОД УП', 'КОД №1', 'СЕРТ №1', 'НАЧАЛО №1', 'КОНЕЦ №1', 'КОД №2',
    'СЕРТ №2', 'НАЧАЛО №2', 'КОНЕЦ №2'
    ]

table_data = pd.DataFrame(columns=result_columns)


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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
# CORS.init_app(app, resources={r'/edit': {'origins': '*'}})
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
        return render_template('home.html', current_user=current_user)
    else:
        read_xlsx_file()
        return redirect(url_for('login'))


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    global table_data
    if request.method == 'GET':
        return render_template('edit.html', data=table_data)
    elif request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Чтение данных из загруженного файла xlsx
                excel_data = pd.read_excel(file)
                # excel_data = excel_data.fillna('')
                # Отображение только необходимых столбцов
                excel_data = excel_data[['Наименование', 'Торговая Марка', 'Количество, шт.', 'Вес БРУТТО, кг.']]
                # Переименование столбцов
                excel_data.columns = ['НАИМЕНОВАНИЕ2', 'ТМ', 'КОЛ-ВО', 'БР']
                # Фильтруем пустые или все NA записи из excel_data перед конкатенацией
                excel_data = excel_data.dropna(how='all')  # Удаляем строки, в которых все записи являются NA
                # Добавление данных в общую таблицу
                if not excel_data.empty:
                    table_data = pd.concat([table_data, excel_data], ignore_index=True)
                    # data = pd.concat([data, excel_data.dropna(how='all')], ignore_index=True)
                    # data = data.append(excel_data, ignore_index=True)

            # Замена значений пустых ячеек с NaN на ''
            table_data = table_data.fillna('')

            # Применение функций чистки к столбцам
            table_data['НАИМЕНОВАНИЕ2'] = table_data['НАИМЕНОВАНИЕ2'].apply(clean_1)  # тут чистка на наличие латиницы
            table_data['ТМ'] = table_data['ТМ'].apply(clean_2)  # тут чистка на наличие кириллицы

            return render_template('edit.html', data=table_data, columns=table_data.columns.tolist())

@app.route('/reg', methods=['GET'])
def reg():
    if request.method == 'GET':
        if User.query.filter_by(name='oleg').first() is None:
            User.register('oleg', '1234')
        return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == 'GET':
        return render_template('login_2.html', form=form)
    else:
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()
            if user is None or not user.verify_password(form.password.data):
                # return redirect(url_for('login', **request.args))
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for('home'))
        return render_template('login_2.html', form=form)


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

#######
# NEW #
#######

# @app.route('/update', methods=['POST'])
# def update_data():
#     global data
#     incoming_data = request.json['data']
#     new_data = pd.DataFrame(incoming_data, columns=result_columns)
#     data = new_data
#     return jsonify({'status': 'OK'})


@app.route('/update', methods=['POST'])
@cross_origin()
def update():
    global table_data
    json_data = request.get_json()
    # if 'data' in json_data:
    #     incoming = json_data['data']
    # else:
    #     # Handle the case where 'data' is not provided. Maybe return an error response.
    #     return jsonify({'status': 'Error', 'message': 'Missing "data" key in the request'}), 400
    # data = update_data(data, incoming)  # Обновляем данные в DataFrame
    # return jsonify({'status': 'OK'})
    # global data
    if not json_data or 'data' not in json_data:
        return jsonify({'error': 'Missing data'}), 400
    else:
        # table_data = json_data.get('data')
        print(f'json_data: {json_data}\n')
        print(f'table_data: {table_data}')
        update_data(table_data, json_data.get('data', {}))
        print(json_data.get('data', {}))
    # data = json_data['data']
    # data = json_data.get('data', {})

    return jsonify({'status': 'OK'})


@app.route('/save', methods=['POST'])
@cross_origin()
def save():
    """
    Сохранение данных в Excel файл и
    Очистка рабочего датафрейма data
    :return:
    """
    global table_data
    table_data.to_excel('Result.xlsx', index=False)
    table_data = pd.DataFrame(columns=result_columns)
    return redirect(url_for('edit'))


##########################################
# logic:
##########################################

@cross_origin()
def update_data(dataframe, incoming_data):
    """
    Функция для обновления данных в DataFrame
    :param dataframe:
    :param incoming_data:
    :return:
    """
    global table_data
    result_columns = dataframe.columns  # Получаем названия столбцов исходного DataFrame
    # updated_dataframe = pd.read_json(incoming_data)
    updated_dataframe = pd.read_json(json.dumps(incoming_data))
    updated_dataframe.columns = result_columns  # Задаем названия столбцов согласно исходному DataFrame
    # updated_dataframe.columns = [result_columns]
    dataframe.update(updated_dataframe)
    table_data = pd.concat([table_data, updated_dataframe], ignore_index=True, sort=False)
    # return jsonify(table_data)
    return table_data.to_json()  # Преобразуем DataFrame в JSON и возвращаем


def clean_1(data):
    """
    Функция для очистки данных в столбце НАИМЕНОВАНИЕ2
    должна возвращать очищенные данные
    """
    cleaned_data = data
    return cleaned_data


def clean_2(data):
    """
    Функция для очистки данных в столбце ТМ
    должна возвращать очищенные данные
    """
    cleaned_data = data
    return cleaned_data


def read_xlsx_file():
    print('reading xlsx..')


def save_xlsx_file():
    print('saving xlsx..')


#######
# NEW #
#######

# def process_excel(file_path, column_name):
#     df = pd.read_excel(file_path)
#     df[column_name] = df[column_name].apply(clean_1(df))
#     return df
#
#
# def save_excel(df, file_path):
#     df.to_excel(file_path, index=False)
