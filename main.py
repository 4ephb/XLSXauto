##########################################
#
# About
#
##########################################

import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship  # , Mapped, mapped_column
# from sqlalchemy.ext.declarative import declarative_base

import pandas as pd

from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
import forms
# from flask_wtf import FlaskForm
from utils import secret_key


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
# Base = declarative_base()
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
        Oдна запись в Certificates может иметь несколько записей в TradeMarks.
        Связана с моделью Certificates через внешний ключ cert_id.
    """
    __tablename__ = 'certificates'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # code: Mapped[str] = mapped_column(String, nullable=False)
    # cert_name: Mapped[str] = mapped_column(String, nullable=False)
    # start_date: Mapped[str] = mapped_column(String, nullable=False)
    # exp_date: Mapped[str] = mapped_column(String, nullable=False)
    # children_1: Mapped[List["TradeMarks"]] = relationship("TradeMarks", back_populates="parent")
    # children_2: Mapped[List["Designations2"]] = relationship("Designations2", back_populates="parent")

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
    Однонаправленная связь - можно получить объект Certificates из объекта Designations2 (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates, связанный с данной записью Designations2.
    """
    __tablename__ = 'designations_2'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # cert_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'), nullable=False)
    # designation: Mapped[str] = mapped_column(String, nullable=False)
    # hscode: Mapped[str] = mapped_column(String, nullable=False)
    # s_low: Mapped[float] = mapped_column(Float, nullable=False)
    # s_high: Mapped[float] = mapped_column(Float)
    # parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'))
    # parent: Mapped["Certificates"] = relationship(back_populates="designations")

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
    Однонаправленная связь - можно получить объект Certificates из объекта TradeMarks (не наоборот).
    Связь определена с помощью атрибута certificate, который указывает на объект Certificates, связанный с данной записью TradeMarks.
    """
    __tablename__ = 'trade_marks'
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # cert_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'), nullable=False)
    # trade_mark: Mapped[str] = mapped_column(String, nullable=False)
    # manufacturer: Mapped[str] = mapped_column(String)
    # category: Mapped[int] = mapped_column(Integer)
    # parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('certificates.id'))
    # parent: Mapped["Certificates"] = relationship(back_populates="trademarks")

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
    # id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    # hscode: Mapped[str] = mapped_column(String, nullable=False)
    # designation: Mapped[str] = mapped_column(String, nullable=False)

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

            # Применение функций чистки на наличие множественных/левых/правых пробелов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].apply(clean_spaces)
            df['ТМ'] = df['ТМ'].apply(clean_spaces)

            # Применение функций чистки на наличие латиницы к данным столбцов
            df['НАИМЕНОВАНИЕ2'] = df['НАИМЕНОВАНИЕ2'].apply(clean_lat_symbols)
            # Применение функций чистки на наличие кириллицы к данным столбцов
            df['ТМ'] = df['ТМ'].apply(clean_cyr_symbols)

            headers = df.columns.tolist()  # Заголовки таблицы входящего файла
            data = df.values.tolist()  # Данные таблицы входящего файла

            # return {'headers': headers, 'data': data}
            return render_template('edit.html', headers=headers, data=data)
            # return redirect(url_for('edit2', headers=headers, data=data))
    else:
        # обработка GET запроса
        # возвращение страницы с формой загрузки файла
        return render_template('edit.html')


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
    # cellData = request_data['cellData']
    rowData = request_data['rowData']
    # headers = request_data['headers']
    headers = request_data.get('headers', [])

    upd_rowData = route_by_columns(rowIndex, colIndex, rowData, headers)

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

    # Запись данных в файл
    df = pd.DataFrame(data, columns=headers)
    df.to_excel('Result_.xlsx', index=False)

    return jsonify({'message': 'Данные успешно сохранены!'})


##########################################
# logic:
##########################################


# def get_tnvd_code(cellData, column_name):
#     tnvd_df = pd.DataFrame(tnvd_names)
#     # Очистка cellData с помощью функции stem_porter
#     cleaned_cellData = stem_porter(cellData)
#     # Итерация по датафрейму tnvd_names и проверка совпадений
#     tnvd_code = ''
#     for index, row in tnvd_df.iterrows():
#         # Очистка names с помощью функции stem_porter
#         cleaned_name = stem_porter(row['names'])
#         if cleaned_name == cleaned_cellData:
#             # Получаем значение 'КОД ТНВД'
#             tnvd_code = tnvd_df['tnvd'][index]
#             # Преобразование tnvd_code в строку для сериализации в JSON
#             tnvd_code = str(tnvd_code)
#             # print(f"{tnvd_df['names'][index]} => {cleaned_name} == {cleaned_cellData} : {tnvd_code}")
#             break
#     updated_colIndex = get_colIndex_by_colName(column_name)
#     return tnvd_code, updated_colIndex


def get_tnvd_code(colIndex, rowData, headers, column_name, engine):
    # Очистка cellData с помощью функции stem_porter
    cellData = rowData[colIndex]
    stem_cellData = stem_porter(cellData)
    print(f'stem_cellData = {stem_cellData}')

    upd_rowData = rowData

    # Создание сессии
    Session = sessionmaker(bind=engine)
    session = Session()

    # Применение функции stem_porter к каждому значению столбца designation
    cleaned_designation = func.stem_porter(Designations2.designation)
    print()

    # Поиск записей в таблице Designations2, у которых значение поля designation после применения функции stem_porter совпадает с очищенным значением cellData
    matching_cert_ids = session.query(Designations2.cert_id).filter(cleaned_designation == stem_cellData).distinct().all()

    # Вывод найденных значений cert_id в консоль
    for cert_id in matching_cert_ids:
        print(cert_id[0])


    # designations_2_data = db.session.execute(db.select(Designations2).order_by(Designations2.hscode)).scalars()
    # for value in designations_2_data:
    #     print("{:<5} {:<3} {:<55} {:<11} {:<5} {:<5}".format(value.id, value.cert_id, value.designation, value.hscode, value.s_low, value.s_high))
    #     # print(f'{value.id}\t{value.cert_id}\t{value.designation}\t{value.hscode}\t{value.s_low}\t{value.s_high}')


    # Получение всех записей из таблицы "designations_2" с совпадающим значением "designation"
    # matching_designations = session.query(Designations2).filter(Designations2.designation == cleaned_cellData).all()
    # matching_designations = session.query(Designations2).filter(cleaned_designation == cleaned_cellData).all()
    # matching_designations = session.query(Designations2).filter(func.stem_porter(Designations2.designation) == cleaned_cellData).all()

    # Итерация по совпавшим записям и вывод значений
    # for designation in matching_designations:
    #     certificates_id = designation.cert_id
    #     designations_2_id = designation.cert_id
    #     hscode = designation.hscode
    #     print(f"Совпавшее значение id из таблицы certificates: {certificates_id}")
    #     print(f"Значение cert_id из таблицы designations_2: {designations_2_id}")
    #     print(f"Значение hscode из таблицы designations_2: {hscode}")
    #     upd_rowData = string_collector(rowData, hscode, column_name, headers)

    # Закрытие сессии
    session.close()
    return upd_rowData


@event.listens_for(engine, "connect")
def sqlite_connect(dbapi_conn, conn_record):
    dbapi_conn.create_function("stem_porter", 1, stem_porter)


def string_collector(rowData, value, col_name, headers):
    index = get_colIndex_by_colName(col_name, headers)
    rowData[index] = value
    return rowData


def route_by_columns(rowIndex, colIndex, rowData, headers):
    """
    В зависимости от имени редактируемой колонки,
    применять определенный набор функций.
    :return: (upd_colIndex), (upd_rowData),
    """
    # Получаем Имя колонки отредактированной ячейки
    col_name = get_colName_by_colIndex(colIndex, headers)

    # Если редактировали значение в колонке 'НАИМЕНОВАНИЕ2',
    upd_rowData = []
    if col_name == 'НАИМЕНОВАНИЕ2':
        # то получаем 'КОД ТНВД' и индекс колонки
        print(col_name)
        print(rowData)
        upd_rowData = get_tnvd_code(colIndex, rowData, headers, 'КОД ТНВД', engine)
        print(f'{upd_rowData}')
    if col_name == 'ТМ':
        rowData[0] = '+' + rowData[0]
        upd_rowData = rowData
    else:
        return rowData

    upd_rowIndex = rowIndex
    upd_colIndex = colIndex
    print(f'Col: {upd_colIndex} | Row: {upd_rowIndex}')
    print(f'{upd_rowData}')
    return upd_rowData


def get_colIndex_by_colName(colName, headers):
    """
    Получаем Индекс колонки по Заголовоку колонки
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
    # Определяем датафрейм result_df с заголовками result_column_headers
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
    cleaned_data = data
    return cleaned_data


def clean_cyr_symbols(data):
    """
    Функция для очистки данных в столбце ТМ
    на наличие символов кириллицы
    должна возвращать очищенные данные
    """
    cleaned_data = data
    return cleaned_data


def clean_spaces(data):
    """
        Функция для очистки данных в строковых столбцах
        на наличие множественных/левых/правых пробелов
        должна возвращать очищенные данные
        """
    cleaned_data = data
    return cleaned_data


def stem_porter(data):
    """
        Функция для очистки данных в строковых столбцах
        Стеммер Портера
        должна возвращать очищенные данные
        """
    cleaned_data = data.lower()
    return cleaned_data





if __name__ == '__main__':
    app.run()
