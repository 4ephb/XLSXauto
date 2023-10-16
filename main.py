##########################################
#
# About
#
##########################################

import os
import re
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship  # , Mapped, mapped_column

import pandas as pd

from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
import forms
# from flask_wtf import FlaskForm
from utils import secret_key
import random

from modules.PorterStemmerRU import PorterStemmerRU

##########################################
# init:
##########################################
class Base(DeclarativeBase):
    pass


app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

app.secret_key = 'secret'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db/main.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(model_class=Base)
# db = SQLAlchemy()
# Base = db.Model

bootstrap = Bootstrap()
login_manager = LoginManager()

# Initialize extensions
bootstrap.init_app(app)
db.init_app(app)
login_manager.init_app(app)
# CORS.init_app(app, resources={r'/edit': {'origins': '*'}})
secret_key(app)

login_manager.login_view = 'login'

# Создание подключения к базе данных
engine = create_engine('sqlite:///' + os.path.join(basedir, 'db/main.db'))


##########################################
# models:
##########################################

class Certificates(Base):
    """
    PARENT
    CHILD_1: Designations2
        Одна запись в Certificates может иметь несколько записей в Designations2.
        Связана с моделью Certificates через внешний ключ cert_id.

    CHILD_2: TradeMarks
        Одна запись в Certificates может иметь несколько записей в TradeMarks.
        Связана с моделью Certificates через внешний ключ cert_id.
    """
    __tablename__ = 'certificates'
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False)
    cert_name = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    exp_date = Column(String, nullable=False)
    designations = relationship("Designations2", back_populates="certificate")
    trademarks = relationship("TradeMarks", back_populates="certificate")


class Designations2(Base):
    """
    CHILD_1
    PARENT: Certificates
    Связана с моделью Certificates через внешний ключ cert_id.
    Одна запись в Designations2 может быть связана с одной записью в Certificates.
    Однонаправленная связь: получить объект Certificates из объекта Designations2 (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates,
    связанный с данной записью Designations2.
    """
    __tablename__ = 'designations_2'
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    cert_id = Column(Integer, ForeignKey('certificates.id'), nullable=False)
    designation = Column(String, nullable=False)
    hscode = Column(String, nullable=False)
    s_low = Column(Float, nullable=False)
    s_high = Column(Float, nullable=False)
    certificate = relationship("Certificates", back_populates="designations")


class TradeMarks(Base):
    """
    CHILD_2
    PARENT: Certificates
    Связана с моделью Certificates через внешний ключ cert_id.
    Одна запись в TradeMarks может быть связана с одной записью в Certificates.
    Однонаправленная связь: получить объект Certificates из объекта TradeMarks (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates,
    связанный с данной записью TradeMarks.
    """
    __tablename__ = 'trade_marks'
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    cert_id = Column(Integer, ForeignKey('certificates.id'), nullable=False)
    trade_mark = Column(String, nullable=False)
    manufacturer = Column(String)
    category = Column(Integer)
    certificate = relationship("Certificates", back_populates="trademarks")


class Designations1(Base):
    """
    Модель Designations1 не имеет связей с другими моделями.
    """
    __tablename__ = 'designations_1'
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    hscode = Column(String, nullable=False)
    designation = Column(String, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # name: Mapped[str] = mapped_column(String, index=True, unique=True)
    # password_hash: Mapped[str] = mapped_column(String(255))

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
        # names = db.session.execute(db.select(TNVDName).order_by(TNVDName.id)).scalars()
        # print(*names)
        return render_template('home.html', current_user=current_user)
    else:
        return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)  # Чтение данных из загруженного файла xlsx
            df = create_result_df(df)  # Преобразуем входящую таблицу в result таблицу

            # Применение функций чистки на наличие латиницы к данным столбцов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].astype(str).apply(clean_lat_symbols)
            # Применение функций чистки на наличие кириллицы к данным столбцов
            df['ТМ'] = df['ТМ'].astype(str).apply(clean_cyr_symbols)

            # Применение функций чистки на наличие множественных/левых/правых пробелов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].map(clean_spaces)
            df['ТМ'] = df['ТМ'].map(clean_spaces)

            # Проходим по значениям колонки 'НАИМЕНОВАНИЕ2' и обновляем данные с помощью update()
            for index, row in df.iterrows():
                col_index = df.columns.get_loc('НАИМЕНОВАНИЕ2')
                request_data = {
                    'rowIndex': index,
                    'colIndex': col_index,
                    'rowData': row.tolist(),
                    'headers': df.columns.tolist()
                }
                # Вызываем функцию update() и получаем обновленную строку
                with app.test_request_context(json=request_data, method='POST'):
                    updated_row_data = update().get_json()['rowData']
                df.loc[index] = updated_row_data

            headers = df.columns.tolist()  # Заголовки таблицы входящего файла
            data = df.values.tolist()  # Данные таблицы входящего файла

            # return {'headers': headers, 'data': data}
            return render_template('edit.html', headers=headers, data=data)
            # return redirect(url_for('edit2', headers=headers, data=data))
    else:
        # обработка GET запроса
        # возвращение страницы с формой загрузки файла
        return render_template('edit.html')


@app.route('/upload_2', methods=['GET', 'POST'])
@login_required
def upload_2():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)  # Чтение данных из загруженного файла xlsx
            df = create_result_df(df)  # Преобразуем входящую таблицу в result таблицу

            # Применение функций чистки на наличие латиницы к данным столбцов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].astype(str).apply(clean_lat_symbols)
            # Применение функций чистки на наличие кириллицы к данным столбцов
            df['ТМ'] = df['ТМ'].astype(str).apply(clean_cyr_symbols)

            # Применение функций чистки на наличие множественных/левых/правых пробелов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].map(clean_spaces)
            df['ТМ'] = df['ТМ'].map(clean_spaces)

            # Проходим по значениям колонки 'НАИМЕНОВАНИЕ2' и обновляем данные с помощью update()
            for index, row in df.iterrows():
                col_index = df.columns.get_loc('НАИМЕНОВАНИЕ2')
                request_data = {
                    'rowIndex': index,
                    'colIndex': col_index,
                    'rowData': row.tolist(),
                    'headers': df.columns.tolist()
                }
                # Вызываем функцию update() и получаем обновленную строку
                with app.test_request_context(json=request_data, method='POST'):
                    updated_row_data = update().get_json()['rowData']
                df.loc[index] = updated_row_data

            headers = df.columns.tolist()  # Заголовки таблицы входящего файла
            data = df.values.tolist()  # Данные таблицы входящего файла

            return render_template('edit_hot.html', headers=headers, data=data)
    else:
        # обработка GET запроса
        # возвращение страницы с формой загрузки файла
        return render_template('edit_hot.html')


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


@app.route('/reg', methods=['GET'])
def reg():
    if request.method == 'GET':
        if User.query.filter_by(name='oleg').first() is None:
            User.register('oleg', '1234')
        return redirect(url_for('home'))


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

@app.route('/update', methods=['POST'])
@login_required
@cross_origin()
def update():
    request_data = request.get_json(force=True)
    rowIndex = int(request_data['rowIndex'])
    colIndex = int(request_data['colIndex'])
    cellData = request_data.get('cellData')
    rowData = request_data['rowData']
    # headers = request_data['headers']
    headers = request_data.get('headers', [])

    upd_rowData = route_by_columns(rowIndex, colIndex, cellData, rowData, headers)
    # upd_rowData = route_by_columns(rowIndex, colIndex, rowData, headers)

    # Создание ответа с обновленными данными
    response_data = {'status': 'success', 'rowIndex': rowIndex, 'rowData': upd_rowData}

    return jsonify(response_data)


@app.route('/save', methods=['POST'])
@login_required
@cross_origin()
def save():
    """
    Сохранение данных в Excel файл и
    :return: JSON response
    """
    # Получить заголовки
    headers = request.form.get('headers')
    headers = json.loads(headers)

    # Получить данные со страницы
    data = request.form.get('data')
    data = json.loads(data)

    print(f'\nHeaders: {headers}')
    print(f'Data: {data}')

    # Запись данных в файл
    df = pd.DataFrame(data, columns=headers[:31])  # Этот срез надо полностью устранить. request тянет 62 заголовка.
    df.to_excel('Result_.xlsx', index=False)

    return jsonify({'message': 'Данные успешно сохранены!'})


##########################################
# logic:
##########################################


def get_cert_info(engine, headers, rowData, naim_value, tm_value):
    # Применяем функцию convert_character_to_space к значениям naim_value и tm_value
    cleaned_naim_value = convert_character_to_space(naim_value)
    cleaned_tm_value = convert_character_to_space(tm_value).lower()

    # Чистка данных с помощью функции stem_porter()
    cleaned_naim_value = stem_porter(cleaned_naim_value)
    # stem_tm_value = stem_porter(cleaned_tm_value)

    # Чистка данных с помощью функции clean_all_spaces()
    cleaned_tm_value = clean_all_spaces(cleaned_tm_value)

    print(f'cleaned_naim_value = {cleaned_naim_value}')
    print(f'cleaned_tm_value = {cleaned_tm_value}\n')

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Применяем функцию convert_character_to_space к каждому значению столбца Designations2.designation и TradeMarks.trade_mark
    cleaned_designation = func.convert_character_to_space(Designations2.designation)
    cleaned_trademarks = func.convert_character_to_space(TradeMarks.trade_mark)
    # Применяем функцию stem_porter к каждому значению столбца Designations2.designation и TradeMarks.trade_mark
    stem_designation = func.stem_porter(cleaned_designation)
    stem_trademarks = func.stem_porter(cleaned_trademarks)
    # Применяем функцию clean_all_spaces к каждому значению столбца TradeMarks.trade_mark
    cleaned_trademarks = func.clean_all_spaces(stem_trademarks)

    # Ну это алхимия)))
    matching_records = session.query(Designations1.designation,
                                     Designations2.designation,
                                     TradeMarks.manufacturer,
                                     TradeMarks.trade_mark,
                                     Designations2.hscode,
                                     Designations2.s_low,
                                     Designations2.s_high,
                                     Certificates.code,
                                     Certificates.cert_name,
                                     Certificates.start_date,
                                     Certificates.exp_date,
                                     TradeMarks.category).join(
        TradeMarks, Designations2.cert_id == TradeMarks.cert_id).join(
        Certificates, Designations2.cert_id == Certificates.id).join(
        Designations1, Designations1.hscode == Designations2.hscode).filter(
        stem_designation == cleaned_naim_value,
        cleaned_trademarks == cleaned_tm_value).distinct().all()

    # Вывод найденных значений в консоль
    if len(matching_records) > 0:
        for record in matching_records:
            print(f'{record}\n')
    else:
        print('Не найдено совпадающих записей!')
        return rowData

    # Получаем правильный $/КГ в зависимости от TradeMarks.category
    matching_records = get_coefficient(matching_records)

    # Вывод отсортированных значений в консоль
    if len(matching_records) > 0:
        for record in matching_records:
            print(f'{record} ')

    # Заголовки таблицы в которых необходимо заменить полученные значения
    data_headers = ['НАИМЕНОВАНИЕ1', 'НАИМЕНОВАНИЕ2', 'ИЗГОТОВИТЕЛЬ', 'ТМ', 'КОД ТНВД', '$/КГ', 'КОД №1', 'СЕРТ №1', 'НАЧАЛО №1', 'КОНЕЦ №1']
    # Подставляем значения в правильное место наполняемой строки
    upd_rowData = string_collector(rowData, headers, matching_records, data_headers)

    # Смотрим данные из Designations2
    # designations_2_data = db.session.execute(db.select(Designations2).order_by(Designations2.hscode)).scalars()
    # for value in designations_2_data:
    #     print("{:<5} {:<3} {:<55} {:<11} {:<5} {:<5}".format(value.id, value.cert_id, value.designation, value.hscode, value.s_low, value.s_high))
    #     # print(f'{value.id}\t{value.cert_id}\t{value.designation}\t{value.hscode}\t{value.s_low}\t{value.s_high}')

    # Закрытие сессии
    session.close()
    return upd_rowData


def get_coefficient(matching_records):
    new_records = []
    for record in matching_records:
        if record[11] == 0:
            new_record = record[:6] + record[7:11]
        else:
            new_record = record[:5] + record[6:11]
        new_records.append(new_record)
    return new_records[0]


@event.listens_for(engine, "connect")
def sqlite_connect(dbapi_conn, conn_record):
    dbapi_conn.create_function("stem_porter", 1, stem_porter)
    dbapi_conn.create_function("convert_character_to_space", 1, convert_character_to_space)
    dbapi_conn.create_function("clean_all_spaces", 1, clean_all_spaces)


def string_collector(rowData, headers, values, col_names):
    indexes = []
    for header in col_names:
        if header in headers:
            indexes.append(headers.index(header))
    print(indexes)
    # for index in indexes:
    #     rowData[index] = '+'
    for index, value in zip(indexes, values):
        rowData[index] = value
    return rowData


def calculations(headers, rowData, quantity_value, gross_value, skg_value):
    """
    Последний шаг для заполнения строки
    :return: upd_rowData
    """
    quantity_value = int(quantity_value)
    if isinstance(gross_value, str):
        gross_value = float(gross_value.replace(',', '.'))
    if skg_value:
        skg_value = float(skg_value.replace(',', '.'))
    else:
        return rowData
    # print(f'\n{quantity_value} {type(quantity_value)}')
    # print(f'{gross_value} {type(gross_value)}')
    # print(f'{skg_value} {type(skg_value)}')
    random.seed(42)
    net_value = gross_value * random.uniform(0.8911111111111111, 0.9111111111111111)
    # net_value = gross_value * (random.random() * 0.02 + 0.8911111111111111)
    cost = net_value * skg_value
    unit_weight = net_value / quantity_value

    n = 2
    # unit_weight = str(round(unit_weight, n)).replace('.', ',')
    # gross_value = str(round(gross_value, n)).replace('.', ',')
    # net_value = str(round(net_value, n)).replace('.', ',')
    # skg_value = str(round(skg_value, n)).replace('.', ',')
    # cost = str(round(cost, n)).replace('.', ',')

    unit_weight = str(round(unit_weight, n))
    gross_value = str(round(gross_value, n))
    net_value = str(round(net_value, n))
    skg_value = str(round(skg_value, n))
    cost = str(round(cost, n))

    digits = [quantity_value, unit_weight, gross_value, net_value, skg_value, cost]
    print(f'\n{digits}')
    # Заголовки таблицы в которых необходимо заменить полученные значения
    data_headers = ['КОЛ-ВО', 'ВЕС ШТ', 'БР', 'НТ', '$/КГ', 'ЦЕНА']
    # Подставляем значения в правильное место наполняемой строки
    upd_rowData = string_collector(rowData, headers, digits, data_headers)
    return upd_rowData


def autofill(headers, rowData):
    '''
    Значения по-умолчанию, которые заполняются автоматически
    '''
    spt = 'KR'
    code = 796
    measure_units = 'шт'
    avaible = 1
    kod_up = '4D'
    autofill_data = [spt, code, measure_units, avaible, kod_up]
    # Заголовки таблицы в которых необходимо заменить полученные значения
    data_headers = ['СПТ', 'КОД', 'НАИМ', 'ЕСТЬ/НЕТ', 'КОД УП']
    # Подставляем значения в правильное место наполняемой строки
    upd_rowData = string_collector(rowData, headers, autofill_data, data_headers)

    return upd_rowData


def route_by_columns(rowIndex, colIndex, cellData, rowData, headers):
# def route_by_columns(rowIndex, colIndex, rowData, headers):
    """
    В зависимости от имени редактируемой колонки,
    применять определенный набор функций.
    :return: upd_rowData
    """
    upd_rowData = rowData

    # Получаем Имя колонки отредактированной ячейки
    col_name = get_colName_by_colIndex(colIndex, headers)

    # Если редактировали значение в колонке 'НАИМЕНОВАНИЕ2' или 'ТМ', то
    if col_name == 'НАИМЕНОВАНИЕ2' or 'ТМ':
        # Получаем значение из НАИМЕНОВАНИЕ2
        naim_index = get_colIndex_by_colName('НАИМЕНОВАНИЕ2', headers)
        naim_value = rowData[naim_index]
        # Получаем значение из ТМ
        tm_index = get_colIndex_by_colName('ТМ', headers)
        tm_value = rowData[tm_index]
        # Получаем значение из КОЛ-ВО
        quantity_index = get_colIndex_by_colName('КОЛ-ВО', headers)
        quantity_value = rowData[quantity_index]
        # Получаем значение из БР
        gross_index = get_colIndex_by_colName('БР', headers)
        gross_value = rowData[gross_index]

        print(f'Редактирование в столбце: {col_name}')
        print(f'Входящие значения строки: {rowData}\n')

        upd_rowData = get_cert_info(engine, headers, rowData, naim_value, tm_value)
        # Получаем значение из $/КГ
        skg_index = get_colIndex_by_colName('$/КГ', headers)
        skg_value = rowData[skg_index]
        upd_rowData = calculations(headers, upd_rowData, quantity_value, gross_value, skg_value)
        upd_rowData = autofill(headers, upd_rowData)
    if col_name == 'КОЛ-ВО':
        # upd_rowData[0] = '+' + upd_rowData[0]
        upd_rowData = quantity_update(colIndex, rowData, cellData, headers)
    else:
        pass

    upd_rowIndex = rowIndex  # rowIndex вообще больше нигде не использую, кроме как посмотреть где редактирование было
    upd_colIndex = colIndex
    print(f'\nСтолбец: {upd_colIndex} | Строка: {upd_rowIndex}')
    print(f'Обновленные значения строки: {upd_rowData}')
    return upd_rowData


def quantity_update(colIndex, rowData, cellData, headers):
    upd_rowData = rowData
    new_cellData = upd_rowData[colIndex]

    print(f'Старое значение: {cellData}')
    print(f'Новое значение {new_cellData}')
    k = int(new_cellData) / int(cellData)
    print(f'Коэффициент: {k}')
    # Получаем значение из БР
    gross_index = get_colIndex_by_colName('БР', headers)
    gross_value = float(rowData[gross_index]) * k
    # Получаем значение из НТ
    net_index = get_colIndex_by_colName('НТ', headers)
    net_value = float(rowData[net_index]) * k

    # unit_index = get_colIndex_by_colName('ВЕС ШТ', headers)
    # unit_weight = float(rowData[unit_index])
    unit_weight = net_value / new_cellData

    skg_index = get_colIndex_by_colName('$/КГ', headers)
    skg_value = float(rowData[skg_index])
    cost = net_value * skg_value

    new_cellData = round(new_cellData, 2)
    unit_weight = round(unit_weight, 2)
    gross_value = round(gross_value, 2)
    net_value = round(net_value, 2)
    cost = round(cost, 2)

    new_data = [new_cellData, unit_weight, gross_value, net_value, cost]
    # Заголовки таблицы в которых необходимо заменить полученные значения
    data_headers = ['КОЛ-ВО', 'ВЕС ШТ', 'БР', 'НТ', 'ЦЕНА']
    # Подставляем значения в правильное место наполняемой строки
    upd_rowData = string_collector(rowData, headers, new_data, data_headers)

    return upd_rowData


def get_colIndex_by_colName(colName, headers):
    """
    Получаем Индекс колонки по Заголовку колонки
    :return: col_index
    """
    # headers = request.form.getlist('headers[]')
    col_index = headers.index(colName)
    return col_index


def get_colName_by_colIndex(colIndex, headers):
    """
    Получаем Заголовок колонки по Индексу колонки
    :return: col_name
    """
    # headers = request.form.getlist('headers[]')
    col_name = headers[colIndex]
    return col_name


def create_result_df(excel_df):
    # Имена колонок Result таблицы
    result_column_headers = [
        'НАИМЕНОВАНИЕ1', 'НАИМЕНОВАНИЕ2', 'ИЗГОТОВИТЕЛЬ', 'ТМ', 'МАРКА', 'МОДЕЛЬ',
        'АРТ', 'СПТ', 'КОЛ-ВО', 'КОД', 'НАИМ', 'КОД ТНВД', 'ДОП КОД', 'ВЕС ШТ',
        'БР', 'НТ', '$/КГ', 'ЦЕНА', 'МЕСТА', 'МЕСТ ЧАСТ', 'ЕСТЬ/НЕТ', 'КОД УП',
        'ДОП КОД УП', 'КОД №1', 'СЕРТ №1', 'НАЧАЛО №1', 'КОНЕЦ №1', 'КОД №2',
        'СЕРТ №2', 'НАЧАЛО №2', 'КОНЕЦ №2'
    ]
    # Определяем dataframe result_df с заголовками result_column_headers
    result_df = pd.DataFrame(columns=result_column_headers)
    # Отображение только необходимых столбцов
    excel_df = excel_df[['Наименование', 'Торговая Марка', 'Количество, шт.', 'Вес БРУТТО, кг.']]
    # Переименование столбцов
    excel_df.columns = ['НАИМЕНОВАНИЕ2', 'ТМ', 'КОЛ-ВО', 'БР']
    # Фильтруем пустые или все NA записи из excel_data перед конкатенацией
    excel_df = excel_df.dropna(how='all')  # Удаляем строки, в которых все записи являются NA
    # Добавление данных в общую таблицу
    if not excel_df.empty:
        result_df = pd.concat([result_df, excel_df], ignore_index=True)
        # Замена значений пустых ячеек с NaN на ''
        result_df = result_df.fillna('')
    # print(result_df)
    return result_df


def clean_lat_symbols(data):
    """
    Функция для очистки данных в столбце НАИМЕНОВАНИЕ2
    на наличие символов латиницы
    должна возвращать очищенные данные
    """
    lat_to_cyr = {
        'A': 'А', 'a': 'а',
        'B': 'В',
        'E': 'Е', 'e': 'е',
        '3': 'з',
        'K': 'К', 'k': 'к',
        'M': 'М',
        'H': 'Н', 'h': 'н',
        'O': 'О', 'o': 'о',
        'P': 'Р', 'p': 'р',
        'C': 'С', 'c': 'с',
        'T': 'Т', 't': 'т',
        'Y': 'У', 'y': 'у',
        'X': 'Х', 'x': 'х',
        'b': 'ь',
        'n': 'п'}

    if pd.isnull(data) or data == 'nan':
        return ''
    else:
        data = re.sub(r'[a-zA-Z3]', lambda x: lat_to_cyr.get(x.group(), x.group()), data)
        # data = re.sub(r'[a-zA-Z]', lambda x: lat_to_cyr[x.group()], data)
        # print(f'lat_to_cyr: {data}')
        return data


def clean_cyr_symbols(data):
    """
    Функция для очистки данных в столбце ТМ
    на наличие символов кириллицы
    должна возвращать очищенные данные
    """
    cyr_to_lat = {
        'А': 'A', 'а': 'a',
        'В': 'B',
        'С': 'C', 'с': 'c',
        'Е': 'E', 'е': 'e',
        'Н': 'H', 'н': 'h',
        'К': 'K', 'к': 'k',
        'М': 'M',
        'О': 'O', 'о': 'o',
        'Р': 'P', 'р': 'p',
        'Т': 'T', 'т': 't',
        'Х': 'X', 'х': 'x',
        'У': 'Y', 'у': 'y',
        'п': 'n',
        'ь': 'b'}

    if pd.isnull(data) or data == 'nan':
        return ''
    else:
        data = re.sub(r'[а-яА-Я]', lambda x: cyr_to_lat.get(x.group(), x.group()), data)
        # data = re.sub(r'[а-яА-Я]', lambda x: cyr_to_lat[x.group()], data)
        # print(f'cyr_to_lat: {data}')
        return data


def clean_spaces(data):
    """
    Функция для очистки данных в строковых столбцах
    на наличие множественных/левых/правых пробелов
    должна возвращать очищенные данные
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # Проверяем, является ли data строкой
        if isinstance(data, str):
            # Удаляем начальные и конечные пробелы
            data = data.strip()
            if ' ' in data:
                # Замена множественных пробелов на один пробел
                data = ' '.join(data.split())
        # print(f'clean_spaces: {data}')
        return data


def clean_all_spaces(data):
    """
    Функция для очистки данных в строковых столбцах
    от всех имеющихся пробелов
    должна возвращать очищенные данные
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # Проверяем, является ли data строкой
        if isinstance(data, str):
            data = data.replace(' ', '')
        return data


def convert_character_to_space(data):
    """
    Функция для очистки данных в строковых столбцах.
    Преобразовывает все спецсимволы в одинарный пробел.
    Должна возвращать очищенные данные.
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # Проверяем, является ли data строкой
        if isinstance(data, str):
            # pattern = r'[^0-9]+'
            pattern = r'[^\w\s]'
            data = re.sub(pattern, ' ', data)
        # print(f'clean_spaces: {data}')
        return data


def stem_porter(data):
    """
    Функция для очистки данных в строковых столбцах
    Стемм Портера
    должна возвращать очищенные данные
    """
    # Создание экземпляра класса PorterStemmerRU
    stemmer = PorterStemmerRU()
    # Предварительная проверка типа значения. Если число, то пропускаем, иначе применяем стемм Портера
    if isinstance(data, float):
        return data
    else:
        return ' '.join([stemmer.stem(word) for word in data.split()])
    # cleaned_data = data.lower()
    # return cleaned_data
