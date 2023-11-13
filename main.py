# -*- coding: cp1251 -*-
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

from xmltodict import parse
import requests
from decimal import Decimal, ROUND_UP

import openpyxl
import xlsxwriter

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

# �������� ����������� � ���� ������
engine = create_engine('sqlite:///' + os.path.join(basedir, 'db/main.db'))


##########################################
# models:
##########################################

class Certificates(Base):
    """
    PARENT
    CHILD_1: Designations2
        ���� ������ � Certificates ����� ����� ��������� ������� � Designations2.
        ������� � ������� Certificates ����� ������� ���� cert_id.

    CHILD_2: TradeMarks
        ���� ������ � Certificates ����� ����� ��������� ������� � TradeMarks.
        ������� � ������� Certificates ����� ������� ���� cert_id.
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
    ������� � ������� Certificates ����� ������� ���� cert_id.
    ���� ������ � Designations2 ����� ���� ������� � ����� ������� � Certificates.
    ���������������� �����: �������� ������ Certificates �� ������� Designations2 (�� ��������).
    ����� ���������� � ������� �������� certificate, ������� ��������� �� ������ Certificates,
    ��������� � ������ ������� Designations2.
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
    ������� � ������� Certificates ����� ������� ���� cert_id.
    ���� ������ � TradeMarks ����� ���� ������� � ����� ������� � Certificates.
    ���������������� �����: �������� ������ Certificates �� ������� TradeMarks (�� ��������).
    ����� ���������� � ������� �������� certificate, ������� ��������� �� ������ Certificates,
    ��������� � ������ ������� TradeMarks.
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
    ������ Designations1 �� ����� ������ � ������� ��������.
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
            df = pd.read_excel(file)  # ������ ������ �� ������������ ����� xlsx
            df = create_result_df(df)  # ����������� �������� ������� � result �������

            # ���������� ������� ������ �� ������� �������� � ������ ��������
            df['������������2'] = df['������������2'].astype(str).apply(clean_lat_symbols)
            # ���������� ������� ������ �� ������� ��������� � ������ ��������
            df['��'] = df['��'].astype(str).apply(clean_cyr_symbols)

            # ���������� ������� ������ �� ������� �������������/�����/������ ��������
            df['������������2'] = df['������������2'].map(clean_spaces)
            df['��'] = df['��'].map(clean_spaces)

            # �������� �� ��������� ������� '������������2' � ��������� ������ � ������� update()
            for index, row in df.iterrows():
                col_index = df.columns.get_loc('������������2')
                request_data = {
                    'rowIndex': index,
                    'colIndex': col_index,
                    'rowData': row.tolist(),
                    'headers': df.columns.tolist()
                }
                # �������� ������� update() � �������� ����������� ������
                with app.test_request_context(json=request_data, method='POST'):
                    updated_row_data = update().get_json()['rowData']
                df.loc[index] = updated_row_data

            headers = df.columns.tolist()  # ��������� ������� ��������� �����
            data = df.values.tolist()  # ������ ������� ��������� �����

            # return {'headers': headers, 'data': data}
            return render_template('edit.html', headers=headers, data=data)
            # return redirect(url_for('edit2', headers=headers, data=data))
    else:
        # ��������� GET �������
        # ����������� �������� � ������ �������� �����
        return render_template('edit.html')


@app.route('/upload_2', methods=['GET', 'POST'])
@login_required
def upload_2():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            df = pd.read_excel(file)  # ������ ������ �� ������������ ����� xlsx
            df = create_result_df(df)  # ����������� �������� ������� � result �������
            # ���������� ������� ������ �� ������� �������� � ������ ��������
            df['������������2'] = df['������������2'].astype(str).apply(clean_lat_symbols)
            # ���������� ������� ������ �� ������� ��������� � ������ ��������
            df['��'] = df['��'].astype(str).apply(clean_cyr_symbols)
            # ���������� ������� ������ �� ������� �������������/�����/������ ��������
            df['������������2'] = df['������������2'].map(clean_spaces)
            df['��'] = df['��'].map(clean_spaces)
            # �������� �� ��������� ������� '������������2' � ��������� ������ � ������� update()
            for index, row in df.iterrows():
                col_index = df.columns.get_loc('������������2')
                request_data = {
                    'rowIndex': index,
                    'colIndex': col_index,
                    'rowData': row.tolist(),
                    'headers': df.columns.tolist()
                }
                # �������� ������� update() � �������� ����������� ������
                with app.test_request_context(json=request_data, method='POST'):
                    updated_row_data = update().get_json()['rowData']
                df.loc[index] = updated_row_data
            headers = df.columns.tolist()  # ��������� ������� ��������� �����
            data = df.values.tolist()  # ������ ������� ��������� �����
            # headers = headers[1:33]
            return render_template('edit_hot.html', headers=headers, data=data)
    else:
        # ��������� GET �������
        # ����������� �������� � ������ �������� �����
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
    rowIndex = request_data['rowIndex']
    colIndex = request_data['colIndex']
    newValue = request_data.get('newValue')
    rowData = request_data['rowData']
    headers = request_data.get('headers', [])
    oldValue = request_data.get('oldValue')
    print(oldValue)
    print(rowData[colIndex])
    print(newValue)
    # headers = request_data['headers']

    # # ���������, ���� �� ������ ��� ���������
    # if rowData[colIndex] == oldValue:
    # # if newValue == oldValue:
    #     print(f'������ �� �����������!')
    #     return jsonify({'success': True})

    print(f'������: {rowIndex + 1} | �������: {colIndex + 1}\n'
          f'������ ����������: {headers}\n'
          f'������ {rowIndex + 1}-� ������: {rowData}\n'
          f'������ ������: {newValue}')

    upd_rowData = route_by_columns(rowIndex, colIndex, newValue, rowData, headers)
    # �������� ������ � ������������ �������
    response_data = {'status': 'success', 'rowIndex': rowIndex, 'rowData': upd_rowData}
    # response_data = json.dumps(response_data)
    return jsonify(response_data)


@app.route('/download', methods=['POST'])
@login_required
@cross_origin()
def download():
    """
    ���������� ������ � Excel ���� �
    :return: JSON response
    """
    if request.method == 'POST':
        # ��������� ����������
        headers = request.form.get('headers')
        headers = json.loads(headers)

        # ��������� ������ �������
        data = request.form.get('data')
        data = json.loads(data)

        # # ����� � �������
        # print(f'\nHeaders: {headers}')
        # print(f'Data: {data}')

        df = pd.DataFrame(data, columns=headers)
        df.to_excel('Result_.xlsx', engine='xlsxwriter', index=False)

        # output = io.BytesIO()
        # writer = pd.ExcelWriter(output, engine='xlsxwriter')
        # df.to_excel(writer, sheet_name='Sheet1', index=False)
        # writer.save()
        # output.seek(0)

        return jsonify({'message': '������ ������� ���������!'})
        # return send_file(output, as_attachment=True, download_name='output.xlsx')


@app.route('/save', methods=['POST'])
@login_required
@cross_origin()
def save():
    """
    ���������� ������ � Excel ���� �
    :return: JSON response
    """
    # �������� ���������
    headers = request.form.get('headers')
    headers = json.loads(headers)

    # �������� ������ �� ��������
    data = request.form.get('data')
    data = json.loads(data)

    print(f'\nHeaders: {headers}')
    print(f'Data: {data}')

    # ������ ������ � ����
    df = pd.DataFrame(data, columns=headers[:32])  # ���� ���� ���� ��������� ���������. request ����� 64 ���������.
    df.to_excel('Result_.xlsx', index=False)

    return jsonify({'message': '������ ������� ���������!'})


curr_coeff = 1


@app.route('/convert_currency', methods=['POST'])
@login_required
@cross_origin()
def convert_currency():
    global curr_coeff
    default_currency_code = 'USD'
    rates = get_rates()
    # currency_code = request.form.get('currency', default=default_currency_code)
    request_data = request.get_json(force=True)
    currency_code = request_data.get('currency')
    headers = request_data.get('headers', [])
    data = request_data.get('data')

    # ����������� ���� ������ � �������
    rate = rates[currency_code]['Value'] / rates[default_currency_code]['Value']
    if currency_code == 'KRW' and default_currency_code == 'USD':
        rate = rate / 1000
    if currency_code == 'JPY' and default_currency_code == 'USD':
        rate = rate / 100
    curr_coeff = rate

    print(f'{currency_code}\{default_currency_code}: {rate}')

    print(currency_code)
    print(headers)
    print(data)

    # # �������� ���������
    # headers = request.form.get('headers')
    # headers = json.loads(headers)
    # print(f'rthygrthsrth{headers}')
    #
    # # �������� ������ �� ��������
    # data = request.form.get('data')
    # data = json.loads(data)

    # ������ ������ � DF
    df = pd.DataFrame(data, columns=headers)

    # print(f'\nHeaders: {headers}')
    # print(f'Data: {data}')

    # # ����� ����������
    # print("���������:")
    # for header in headers:
    #     print(header)
    #
    # # ����� ������
    # print("������:")
    # print(df)

    data_rows = []
    for index, row in df.iterrows():
        quantity = row['���-��']
        gross_weight = row['��']
        price_per_kg = row['$/��']
        updated_row_data = calculations(headers, row, quantity, gross_weight, price_per_kg)
        data_rows.append(updated_row_data)


    updated_df = pd.DataFrame(data_rows, columns=headers)

    # for index, row in updated_df.iterrows():
    #     col_index = updated_df.columns.get_loc('������������2')
    #     request_data = {
    #         'rowIndex': index,
    #         'colIndex': col_index,
    #         'rowData': row.tolist(),
    #         'headers': updated_df.columns.tolist()
    #     }
    #     with app.test_request_context(json=request_data, method='POST'):
    #         updated_row_data = update().get_json().get('rowData')
    #     updated_df.loc[index] = updated_row_data

    headers = updated_df.columns.tolist()  # ��������� ������� ��������� �����
    data = updated_df.values.tolist()  # ������ ������� ��������� �����
    result = {'headers': headers, 'data': data}
    # print(result)
    return jsonify(result)


##########################################
# logic:
##########################################


def get_rates():
    rates = {}
    response = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
    response.encoding = 'cp1251'

    # text = response.text.encode('utf-8').replace('windows-1251', 'utf-8')
    text = response.text.replace('windows-1251', 'utf-8')
    cbr = parse(text)

    rates['date'] = cbr['ValCurs']['@Date']

    for v in cbr['ValCurs']['Valute']:
        v['Value'] = float(v['Value'].replace(',', '.'))
        rates[v['CharCode']] = v

    return rates


def calculate_currency(amount, rate):
    return Decimal(1 / rate * amount).quantize(Decimal('0.01'), rounding=ROUND_UP)


def get_cert_info(engine, headers, rowData, naim_value, tm_value):
    print(f'\n2. �������� ������ �����������:')
    # ��������� ������� convert_character_to_space � ��������� naim_value � tm_value
    cleaned_naim_value = convert_character_to_space(naim_value)
    cleaned_tm_value = convert_character_to_space(tm_value).lower()

    # ������ ������ � ������� ������� stem_porter()
    cleaned_naim_value = stem_porter(cleaned_naim_value)
    # stem_tm_value = stem_porter(cleaned_tm_value)

    # ������ ������ � ������� ������� clean_all_spaces()
    cleaned_tm_value = clean_all_spaces(cleaned_tm_value)

    print(f'\t��������� ������ ��� ������:\n'
          f'\t\t{cleaned_naim_value}\n'
          f'\t\t{cleaned_tm_value}')

    # �������� ������
    Session = sessionmaker(bind=engine)
    session = Session()

    # ��������� ������� convert_character_to_space � ������� �������� ������� Designations2.designation � TradeMarks.trade_mark
    cleaned_designation = func.convert_character_to_space(Designations2.designation)
    cleaned_trademarks = func.convert_character_to_space(TradeMarks.trade_mark)
    # ��������� ������� stem_porter � ������� �������� ������� Designations2.designation � TradeMarks.trade_mark
    stem_designation = func.stem_porter(cleaned_designation)
    stem_trademarks = func.stem_porter(cleaned_trademarks)
    # ��������� ������� clean_all_spaces � ������� �������� ������� TradeMarks.trade_mark
    cleaned_trademarks = func.clean_all_spaces(stem_trademarks)

    # �� ��� �������)))
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

    # ����� ��������� �������� � �������
    if len(matching_records) > 0:
        print('\t������� ����������� ������:')

        i = 1
        for record in matching_records:
            print(f'\t\t{i}. {record}')
            i+= 1

        # �������� ���������� $/�� � ����������� �� TradeMarks.category
        matching_records = get_coefficient(matching_records)
        # ��������� ������� � ������� ���������� �������� ���������� ��������
        data_headers = ['������������1', '������������2', '������������', '��', '��� ����', '$/��', '��� �1', '���� �1',
                        '������ �1', '����� �1']
        # ����������� �������� � ���������� ����� ����������� ������
        upd_rowData = string_collector(rowData, headers, matching_records, data_headers)
        return upd_rowData
    else:
        print('\t�� ������� ����������� �������!')
        data_headers = ['������������1', '������������2', '������������', '��', '��� ����', '$/��', '��� �1', '���� �1',
                        '������ �1', '����� �1']
        matching_records = ['', naim_value, '', tm_value, '', '', '', '', '', '']
        upd_rowData = string_collector(rowData, headers, matching_records, data_headers)
        return upd_rowData

    # ������� ������ �� Designations2
    # designations_2_data = db.session.execute(db.select(Designations2).order_by(Designations2.hscode)).scalars()
    # for value in designations_2_data:
    #     print("{:<5} {:<3} {:<55} {:<11} {:<5} {:<5}".format(value.id, value.cert_id, value.designation, value.hscode, value.s_low, value.s_high))
    #     # print(f'{value.id}\t{value.cert_id}\t{value.designation}\t{value.hscode}\t{value.s_low}\t{value.s_high}')

    # �������� ������
    session.close()



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
    print(f'\t���������� �������� {indexes} ������� {values}')
    # for index in indexes:
    #     rowData[index] = '+'
    for index, value in zip(indexes, values):
        rowData[index] = value
    return rowData


def calculations(headers, rowData, quantity, gross_weight, price_per_kg):
    """
    ��������� ��� ��� ���������� ������
    :return: upd_rowData
    """
    print(f'\n3. ������ ��������� � ����:')
    # ������ quantity, gross_weight, price_per_kg
    # quantity = float(quantity)  # (���-��)
    if quantity and gross_weight:
        quantity = float(quantity)  # (���-��)
        gross_weight = float(gross_weight)  # (��)
    if price_per_kg:
        if isinstance(price_per_kg, str):
            # price_per_kg = float(price_per_kg.replace(',', '.'))  # ($/��)
            price_per_kg = float(price_per_kg.replace(',', '.'))  # ($/��)
        else:
            price_per_kg = float(price_per_kg)  # ($/��)

        # print(f'\n{quantity_value} {type(quantity_value)}')
        # print(f'{gross_value} {type(gross_value)}')
        # print(f'{skg_value} {type(skg_value)}')

        # ������������ ��������������� net_weight
        random.seed(42)
        min_coeff = 0.8911  # 111111111111
        max_coeff = 0.9112  # 111111111111
        coeff = round(random.uniform(min_coeff, max_coeff), 4)
        # coeff = (random.random() * 0.02 + min_coeff)

        # net_weight = round(gross_weight * coeff, 4)  # (��)
        net_weight = Decimal(gross_weight * coeff).quantize(Decimal('0.01'), rounding=ROUND_UP)  # (��)
        # net_weight = float(net_weight)

        converted_currency = Decimal(1 / curr_coeff * price_per_kg).quantize(Decimal('0.01'), rounding=ROUND_UP)
        # converted_currency = round(1 / curr_coeff * price_per_kg, 4)

        # ������������ price
        # price = (price_per_kg * curr_coeff) * net_weight  # (����) ��� ��������� ������������ �� curr_coeff. �� ����
        price = float(converted_currency * net_weight)  # (����)
        price = round(price / quantity, 2) * quantity  # ����� (����)

        # ������������ �������� net_weight
        # net_weight = price / (price_per_kg * curr_coeff)  # (��) ��� ��������� ������������ �� curr_coeff. �� ����
        net_weight = price / float(converted_currency)  # (��)

        # ������������ weight_per_unit
        weight_per_unit = net_weight / quantity  # (��� ��)

        # ������������ price_per_unit
        price_per_unit = price / quantity

        # ����������
        weight_per_unit = float(round(weight_per_unit, 3))  # .replace('.', ',')
        gross_weight = float(round(gross_weight, 2))  # .replace('.', ',')
        net_weight = float(round(net_weight, 2))  # .replace('.', ',')
        price_per_kg = float(round(price_per_kg, 2))  # .replace('.', ',')
        price = float(round(price, 2))  # .replace('.', ',')
        price_per_unit = float(round(price_per_unit, 2))  # .replace('.', ',')
        coeff = float(round(coeff, 4))  # .replace('.', ',')  # ������ ����� ������ �� �����

        # weight_per_unit = str(round(weight_per_unit, 3))
        # gross_weight = str(round(gross_weight, 2))
        # net_weight = str(round(net_weight, 2))
        # price_per_kg = str(round(price_per_kg, 2))
        # price = str(round(price, 2))
        # price_per_unit = round(price_per_unit, 2)
        # coeff = round(coeff, 4)  # ������ ����� ������ �� �����

        # digits = [quantity, weight_per_unit, gross_weight, net_weight, price_per_kg, price]
        digits = [quantity, weight_per_unit, price_per_unit, gross_weight, net_weight, price_per_kg, price]
        # print(f'\n{digits}')
        # ��������� ������� � ������� ���������� �������� ���������� ��������
        # data_headers = ['���-��', '��� ��', '��', '��', '$/��', '����']
        data_headers = ['���-��', '��� ��', '$/��', '��', '��', '$/��', '����']
        # ����������� �������� � ���������� ����� ����������� ������
        upd_rowData = string_collector(rowData, headers, digits, data_headers)
        return upd_rowData
    else:
        digits = [quantity, '', '', gross_weight, '', '', '']
        data_headers = ['���-��', '��� ��', '$/��', '��', '��', '$/��', '����']
        upd_rowData = string_collector(rowData, headers, digits, data_headers)
        return upd_rowData


def autofill(headers, rowData):
    '''
    �������� ��-���������, ������� ����������� �������������
    '''
    print(f'\n4. �������������� ������� ��-���������:')
    skg_index = get_colIndex_by_colName('$/��', headers)
    skg_value = rowData[skg_index]
    if skg_value:
        spt = 'KR'
        code = 796
        measure_units = '��'
        avaible = 1
        kod_up = '4D'
        autofill_data = [spt, code, measure_units, avaible, kod_up]
        # ��������� ������� � ������� ���������� �������� ���������� ��������
        data_headers = ['���', '���', '����', '����/���', '��� ��']
        # ����������� �������� � ���������� ����� ����������� ������
        upd_rowData = string_collector(rowData, headers, autofill_data, data_headers)
        return upd_rowData
    else:
        autofill_data = ['', '', '', '', '']
        data_headers = ['���', '���', '����', '����/���', '��� ��']
        upd_rowData = string_collector(rowData, headers, autofill_data, data_headers)
        return upd_rowData


def route_by_columns(rowIndex, colIndex, cellData, rowData, headers):
# def route_by_columns(rowIndex, colIndex, rowData, headers):
    """
    � ����������� �� ����� ������������� �������,
    ��������� ������������ ����� �������.
    :return: upd_rowData
    """
    upd_rowData = rowData
    # �������� ��� ������� ����������������� ������
    col_name = get_colName_by_colIndex(colIndex, headers)
    print(f'\n1. ������������� ������������� �������:\n'
          f'\t��� �������: {col_name}')
    # ���� ������������� �������� � ������� '������������2' ��� '��', ��
    if col_name == '������������2' or '��':
        # �������� �������� �� ������������2
        naim_index = get_colIndex_by_colName('������������2', headers)
        naim_value = rowData[naim_index]
        # �������� �������� �� ��
        tm_index = get_colIndex_by_colName('��', headers)
        tm_value = rowData[tm_index]
        # �������� �������� �� ���-��
        quantity_index = get_colIndex_by_colName('���-��', headers)
        quantity_value = rowData[quantity_index]
        # �������� �������� �� ��
        gross_index = get_colIndex_by_colName('��', headers)
        gross_value = rowData[gross_index]

        upd_rowData = get_cert_info(engine, headers, rowData, naim_value, tm_value)

        # �������� �������� �� $/��
        skg_index = get_colIndex_by_colName('$/��', headers)
        skg_value = rowData[skg_index]
        upd_rowData = calculations(headers, upd_rowData, quantity_value, gross_value, skg_value)
        upd_rowData = autofill(headers, upd_rowData)
    if col_name == '���-��':
        # upd_rowData[0] = '+' + upd_rowData[0]
        upd_rowData = quantity_update(colIndex, rowData, cellData, headers)
        return upd_rowData
    else:
        pass

    upd_rowIndex = rowIndex  # rowIndex ������ ������ ����� �� ���������, ����� ��� ���������� ��� �������������� ����
    upd_colIndex = colIndex

    print(f'\n5. ����������� �������� ������:\n'
          f'\t{upd_rowData}\n\n')
    return upd_rowData


def quantity_update(colIndex, rowData, cellData, headers):
    upd_rowData = rowData
    quantity = upd_rowData[colIndex]
    print(f'������ ��������: {cellData}')
    print(f'����� �������� {quantity}')
    k = int(quantity) / int(cellData) if int(cellData) != 0 else 1
    print(f'�����������: {k}')
    # �������� �������� �� ��
    gross_index = get_colIndex_by_colName('��', headers)
    # gross_weight = float((rowData[gross_index]).replace(',', '.')) * k
    gross_weight = float((rowData[gross_index])) * k
    # �������� �������� �� ��
    net_index = get_colIndex_by_colName('��', headers)
    # net_weight = float((rowData[net_index]).replace(',', '.')) * k
    print(type(rowData[net_index]))
    n = rowData[net_index]  # if rowData[net_index] else 0.0
    net_weight = float(n) * k
    net_weight = Decimal(net_weight).quantize(Decimal('0.01'), rounding=ROUND_UP)  # (��)
    net_weight = float(net_weight)

    # ������������ weight_per_unit
    # unit_index = get_colIndex_by_colName('��� ��', headers)
    # weight_per_unit = float(rowData[unit_index])
    weight_per_unit = net_weight / quantity   # (��� ��)

    # �������� �������� �� $/��
    price_per_kg_index = get_colIndex_by_colName('$/��', headers)
    # price_per_kg = float((rowData[price_per_kg_index]).replace(',', '.'))
    k = float(rowData[price_per_kg_index])  # if rowData[price_per_kg_index] else 0.0
    price_per_kg = k

    # ������������ price
    converted_currency = Decimal(1 / curr_coeff * price_per_kg).quantize(Decimal('0.01'), rounding=ROUND_UP)
    converted_currency = float(converted_currency)
    price = converted_currency * net_weight  # (����)
    price = round(price / quantity, 2) * quantity  # ����� (����)
    # price = net_weight * price_per_kg  # (����)

    # ������������ �������� net_weight
    net_weight = price / converted_currency
    # if converted_currency != 0:
    #     net_weight = price / converted_currency  # (��)
    # else:
    #     net_weight = 0

    # ������������ price_per_unit
    price_per_unit = price / quantity  # ($/��)

    # ����������
    # quantity = round(quantity, 2)
    weight_per_unit = round(weight_per_unit, 3)
    price_per_unit = round(price_per_unit, 2)
    gross_weight = round(gross_weight, 2)
    net_weight = round(net_weight, 2)
    price = round(price, 2)

    new_data = [quantity, weight_per_unit, price_per_unit, gross_weight, net_weight, price]
    # ��������� ������� � ������� ���������� �������� ���������� ��������
    data_headers = ['���-��', '��� ��', '$/��', '��', '��', '����']
    # ����������� �������� � ���������� ����� ����������� ������
    upd_rowData = string_collector(rowData, headers, new_data, data_headers)

    return upd_rowData


def get_colIndex_by_colName(colName, headers):
    """
    �������� ������ ������� �� ��������� �������
    :return: col_index
    """
    # headers = request.form.getlist('headers[]')
    col_index = headers.index(colName)
    return col_index


def get_colName_by_colIndex(colIndex, headers):
    """
    �������� ��������� ������� �� ������� �������
    :return: col_name
    """
    # headers = request.form.getlist('headers[]')
    col_name = headers[colIndex]
    return col_name


def create_result_df(excel_df):
    # ����� ������� Result �������
    result_column_headers = [
        '������������1', '������������2', '������������', '��', '�����', '������',
        '���', '���', '���-��', '���', '����', '��� ����', '��� ���', '��� ��', '$/��',
        '��', '��', '$/��', '����', '�����', '���� ����', '����/���', '��� ��',
        '��� ��� ��', '��� �1', '���� �1', '������ �1', '����� �1', '��� �2',
        '���� �2', '������ �2', '����� �2'
    ]
    # ���������� dataframe result_df � ����������� result_column_headers
    result_df = pd.DataFrame(columns=result_column_headers)
    # ����������� ������ ����������� ��������
    excel_df = excel_df[['������������', '�������� �����', '����������, ��.', '��� ������, ��.']]
    # �������������� ��������
    excel_df.columns = ['������������2', '��', '���-��', '��']
    # ��������� ������ ��� ��� NA ������ �� excel_data ����� �������������
    excel_df = excel_df.dropna(how='all')  # ������� ������, � ������� ��� ������ �������� NA
    # ���������� ������ � ����� �������
    if not excel_df.empty:
        result_df = pd.concat([result_df, excel_df], ignore_index=True)
        # ������ �������� ������ ����� � NaN �� ''
        result_df = result_df.fillna('')
    # print(result_df)
    return result_df


def clean_lat_symbols(data):
    """
    ������� ��� ������� ������ � ������� ������������2
    �� ������� �������� ��������
    ������ ���������� ��������� ������
    """
    lat_to_cyr = {
        'A': '�', 'a': '�',
        'B': '�',
        'E': '�', 'e': '�',
        '3': '�',
        'K': '�', 'k': '�',
        'M': '�',
        'H': '�', 'h': '�',
        'O': '�', 'o': '�',
        'P': '�', 'p': '�',
        'C': '�', 'c': '�',
        'T': '�', 't': '�',
        'Y': '�', 'y': '�',
        'X': '�', 'x': '�',
        'b': '�',
        'n': '�'}

    if pd.isnull(data) or data == 'nan':
        return ''
    else:
        data = re.sub(r'[a-zA-Z3]', lambda x: lat_to_cyr.get(x.group(), x.group()), data)
        # data = re.sub(r'[a-zA-Z]', lambda x: lat_to_cyr[x.group()], data)
        # print(f'lat_to_cyr: {data}')
        return data


def clean_cyr_symbols(data):
    """
    ������� ��� ������� ������ � ������� ��
    �� ������� �������� ���������
    ������ ���������� ��������� ������
    """
    cyr_to_lat = {
        '�': 'A', '�': 'a',
        '�': 'B',
        '�': 'C', '�': 'c',
        '�': 'E', '�': 'e',
        '�': 'H', '�': 'h',
        '�': 'K', '�': 'k',
        '�': 'M',
        '�': 'O', '�': 'o',
        '�': 'P', '�': 'p',
        '�': 'T', '�': 't',
        '�': 'X', '�': 'x',
        '�': 'Y', '�': 'y',
        '�': 'n',
        '�': 'b'}

    if pd.isnull(data) or data == 'nan':
        return ''
    else:
        data = re.sub(r'[�-��-�]', lambda x: cyr_to_lat.get(x.group(), x.group()), data)
        # data = re.sub(r'[�-��-�]', lambda x: cyr_to_lat[x.group()], data)
        # print(f'cyr_to_lat: {data}')
        return data


def clean_spaces(data):
    """
    ������� ��� ������� ������ � ��������� ��������
    �� ������� �������������/�����/������ ��������
    ������ ���������� ��������� ������
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # ���������, �������� �� data �������
        if isinstance(data, str):
            # ������� ��������� � �������� �������
            data = data.strip()
            if ' ' in data:
                # ������ ������������� �������� �� ���� ������
                data = ' '.join(data.split())
        # print(f'clean_spaces: {data}')
        return data


def clean_all_spaces(data):
    """
    ������� ��� ������� ������ � ��������� ��������
    �� ���� ��������� ��������
    ������ ���������� ��������� ������
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # ���������, �������� �� data �������
        if isinstance(data, str):
            data = data.replace(' ', '')
        return data


def convert_character_to_space(data):
    """
    ������� ��� ������� ������ � ��������� ��������.
    ��������������� ��� ����������� � ��������� ������.
    ������ ���������� ��������� ������.
    """
    if pd.isnull(data) or data == 'nan' or data == '':
        return ''
    else:
        # ���������, �������� �� data �������
        if isinstance(data, str):
            # pattern = r'[^0-9]+'
            pattern = r'[^\w\s]'
            data = re.sub(pattern, ' ', data)
        # print(f'clean_spaces: {data}')
        return data


def stem_porter(data):
    """
    ������� ��� ������� ������ � ��������� ��������
    ����� �������
    ������ ���������� ��������� ������
    """
    # �������� ���������� ������ PorterStemmerRU
    stemmer = PorterStemmerRU()
    # ��������������� �������� ���� ��������. ���� �����, �� ����������, ����� ��������� ����� �������
    if isinstance(data, float):
        return data
    else:
        return ' '.join([stemmer.stem(word) for word in data.split()])
    # cleaned_data = data.lower()
    # return cleaned_data


# if __name__ == '__main__':
#     app.run(debug=False)
