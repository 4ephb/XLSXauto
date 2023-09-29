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
from flask_cors import CORS, cross_origin

##########################################
# init:
##########################################
basedir = os.path.abspath(os.path.dirname(__file__))

# Временные тестовые данные (в дальнейшем удалить)
tnvd_names = [
    {"names": "БАЛЬЗАМ ДЛЯ ГУБ", "tnvd": 3304990000},
    {"names": "ВВ КРЕМ", "tnvd": 3304990000},
    {"names": "СС КРЕМ", "tnvd": 3304990000},
    {"names": "ВОДА ОЧИЩАЮЩАЯ", "tnvd": 3304990000},
    {"names": "ГЕЛЬ ДЛЯ ДУША", "tnvd": 3401300000},
    {"names": "ГЕЛЬ ДЛЯ ТЕЛА", "tnvd": 3304990000},
    {"names": "ГЕЛЬ ДЛЯ УМЫВАНИЯ", "tnvd": 3401300000},
    {"names": "ГИДРОФИЛЬНОЕ МАСЛО", "tnvd": 3304990000},
    {"names": "ЗУБНАЯ ПАСТА", "tnvd": 3306100000},
    {"names": "КАРАНДАШ ДЛЯ ГЛАЗ", "tnvd": 3304200000},
    {"names": "КАРАНДАШ ДЛЯ ГУБ", "tnvd": 3304100000},
    {"names": "КОНДИЦИОНЕР ДЛЯ ВОЛОС", "tnvd": 3305900009},
    {"names": "КРЕМ ДЛЯ ГЛАЗ", "tnvd": 3304990000},
    {"names": "КРЕМ ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "КРЕМ ДЛЯ РУК", "tnvd": 3304990000},
    {"names": "КУШОН", "tnvd": 3304910000},
    {"names": "ЛОСЬОН ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "ЛОСЬОН ДЛЯ ТЕЛА", "tnvd": 3304990000},
    {"names": "МАСКА ГИДРОГЕЛЕВАЯ ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "МАСКА ДЛЯ ВОЛОС", "tnvd": 3305900009},
    {"names": "МАСКА ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "МАСКА ДЛЯ НОГ", "tnvd": 3304990000},
    {"names": "МАСКА ДЛЯ РУК", "tnvd": 3304990000},
    {"names": "МАСКА САЛФЕТКА", "tnvd": 3307900008},
    {"names": "МАСКА-САЛФЕТКА ДЛЯ ЛИЦА", "tnvd": 3307900008},
    {"names": "МАСЛО ГИДРОФИЛЬНОЕ", "tnvd": 3304990000},
    {"names": "МАСЛО ДЛЯ ТЕЛА", "tnvd": 3304990000},
    {"names": "МИСТ ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "МЫЛО", "tnvd": 3401190000},
    {"names": "НАБОР", "tnvd": 3304990000},
    {"names": "НАБОР ДЛЯ ВОЛОС", "tnvd": 3305900009},
    {"names": "НАБОРЫ", "tnvd": 3304990000},
    {"names": "НОЧНАЯ МАСКА ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "ОЧИЩАЮЩАЯ ВОДА", "tnvd": 3401300000},
    {"names": "ПАСТА ЗУБНАЯ", "tnvd": 3306100000},
    {"names": "ПАТЧИ", "tnvd": 3304990000},
    {"names": "ПАТЧИ ДЛЯ ГЛАЗ", "tnvd": 3304990000},
    {"names": "ПЕНКА ДЛЯ УМЫВАНИЯ", "tnvd": 3401300000},
    {"names": "ПЕНКА-ГЕЛЬ ДЛЯ УМЫВАНИЯ", "tnvd": 3401300000},
    {"names": "ПЕНКА-ПОРОШОК ДЛЯ УМЫВАНИЯ", "tnvd": 3401300000},
    {"names": "ПЕЧЕНЬЕ", "tnvd": 1905311500},
    {"names": "ПЛАСТЫРЬ", "tnvd": 3307900008},
    {"names": "ПОДВОДКА ДЛЯ ГЛАЗ", "tnvd": 3304200000},
    {"names": "ПОМАДА", "tnvd": 3304100000},
    {"names": "ПРАЙМЕР", "tnvd": 3304990000},
    {"names": "ПУДРА", "tnvd": 3304910000},
    {"names": "РОЛИКОВЫЙ МЕХАНИЧЕСКИЙ МАССАЖЕР", "tnvd": 9019109009},
    {"names": "СКРАБ", "tnvd": 3304990000},
    {"names": "СОЛЬ ДЛЯ ВАННЫ", "tnvd": 3307300000},
    {"names": "СПРЕЙ ДЛЯ ВОЛОС", "tnvd": 3304990000},
    {"names": "СРЕДСТВО ДЛЯ РЕСНИЦ", "tnvd": 3305900009},
    {"names": "СРЕДСТВО ДЛЯ СНЯТИЯ МАКИЯЖА", "tnvd": 3304990000},
    {"names": "СУТИНГ ГЕЛЬ", "tnvd": 3304990000},
    {"names": "СЫВОРОТКА ДЛЯ ВОЛОС", "tnvd": 3304990000},
    {"names": "СЫВОРОТКА ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "СЫВОРОТКА-ЭССЕНЦИИЯ ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "ТЕЙПЫ", "tnvd": 3307900008},
    {"names": "ТИНТ ДЛЯ ГУБ", "tnvd": 3304100000},
    {"names": "ТОНАЛЬНЫЙ КРЕМ", "tnvd": 3304990000},
    {"names": "ТОНЕР ДЛЯ ЛИЦА", "tnvd": 3304990000},
    {"names": "ТУАЛЕТНОЕ МЫЛО", "tnvd": 3401110009},
    {"names": "ТУШЬ", "tnvd": 3304200000},
    {"names": "ТУШЬ ДЛЯ РЕСНИЦ", "tnvd": 3304200000},
    {"names": "ШАМПУНЬ", "tnvd": 3305100000},
    {"names": "ШАМПУНЬ ДЛЯ ВОЛОС", "tnvd": 3305100000}
    ]

tnvd_description = [
    {"number": 3304990000, "description": "КОСМЕТИЧЕСКОЕ СРЕДСТВО ДЛЯ УХОДА ЗА ЛИЦОМ И ТЕЛОМ, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3307900008, "description": "КОСМЕТИЧЕСКОЕ СРЕДСТВО НА ОСНОВЕ ИЗ НЕТКАНОГО МАТЕРИАЛА ДЛЯ УХОДА ЗА КОЖЕЙ ЛИЦА, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3401300000, "description": "МОЮЩЕЕ СТРЕДСТВО ДЛЯ ЛИЧНОЙ ГИГИЕНЫ, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3304200000, "description": "КОСМЕТИЧЕСКОЕ СРЕДСТВО ДЛЯ МАКИЯЖА ГЛАЗ, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3305100000, "description": "КОСМЕТИЧЕСКОЕ СТРЕДСТВО ДЛЯ УХОДА ЗА ВОЛОСАМИ НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3305900009, "description": "КОСМЕТИЧЕСКОЕ СТРЕДСТВО ДЛЯ УХОДА ЗА ВОЛОСАМИ НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3306100000, "description": "СРЕДСТВО ДЛЯ ГИГИЕНЫ ПОЛОСТИ РТА НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ СОДЕРЖАЩЕЕ ФТОРИДЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ОТБЕЛИВАНИЯ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 9019109009, "description": "РОЛИКОВЫЙ МЕХАНИЧЕСКИЙ МАССАЖЕР ДЛЯ СНЯТИЯ УСТАЛОСТИ."},
    {"number": 3304100000, "description": "КОСМЕТИЧЕСКОЕ СРЕДСТВО ДЕКОРАТИВНОЕ ДЛЯ МАКИЯЖА ЛИЦА, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ СОДЕРЖАЩЕЕ ФТОРИДЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ОТБЕЛИВАНИЯ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3304910000, "description": "КОСМЕТИЧЕСКОЕ СРЕДСТВО ДЛЯ МАКИЯЖА ЛИЦА, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3401190000, "description": "МОЮЩЕЕ СТРЕДСТВО ДЛЯ ЛИЧНОЙ ГИГИЕНЫ В БРУСКАХ, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 3924900009, "description": "ИЗДЕЛИЯ ИЗ ПОЛИМЕРНОГО МАТЕРИАЛА ДЛЯ ДОМАШНЕГО ОБИХОДА."},
    {"number": 6304191000, "description": "ИЗДЕЛИЕ ДЕКОРАТИВНОЕ ГОТОВОЕ ИЗ ТЕКСТИЛЬНЫХ МАТЕРИАЛОВ - ПОКРЫВАЛА ПОСТЕЛЬНЫЕ, ИЗГОТОВЛЕННЫЕ ИЗ ХЛОПЧАТОБУМАЖНЫХ ТКАНЕЙ."},
    {"number": 1905311100, "description": "СЛАДКОЕ СУХОЕ ПЕЧЕНЬЕ ПОЛНОСТЬЮ ИЛИ ЧАСТИЧНО ПОКРЫТОЕ ШОКОЛАДОМ СОДЕРЖАЩИМИ КАКАО, В ПЕРВИЧНЫХ УПАКОВКАХ НЕТТО-МАССОЙ НЕ БОЛЕЕ 85 Г."},
    {"number": 1905311900, "description": "СЛАДКОЕ СУХОЕ ПЕЧЕНЬЕ ПОЛНОСТЬЮ ИЛИ ЧАСТИЧНО ПОКРЫТОЕ ШОКОЛАДОМ СОДЕРЖАЩИМИ КАКАО, В ПЕРВИЧНЫХ УПАКОВКАХ НЕТТО-МАССОЙ БОЛЕЕ 85 Г."},
    {"number": 3402500000, "description": "МОЮЩИЕ И ЧИСТЯЩИЕ СРЕДСТВА, ДЛЯ ХОЗ/БЫТОВЫХ НУЖД, РАСФАСОВАННЫЕ ДЛЯ РОЗНИЧНОЙ ПРОДАЖИ."},
    {"number": 9603210000, "description": "ЩЕТКИ ЗУБНЫЕ ДЛЯ ВЗРОСЛЫХ, ИЗГОТОВЛЕНЫ ИЗ ПОЛИМЕРНЫХ МАТЕРИАЛОВ, СО ЩЕТИНОЙ ИЗ СИНТЕТИЧЕСКОГО ВОРСА."},
    {"number": 3307300000, "description": "СОЛЬ ДЛЯ ВАНН, НЕ СОДЕРЖАЩЕЕ СПИРТ, НАНОМАТЕРИАЛЫ, НЕ ПРЕДНАЗНАЧЕННОЕ ДЛЯ ДЕТЕЙ. КЛАСС ТОВАРА НЕ ПОИМЕНОВАН."},
    {"number": 9404400009, "description": "ПОКРЫВАЛА ДЛЯ КРОВАТЕЙ ПРОЧИЕ:"}
    ]

tnvd_info = pd.DataFrame(tnvd_description)  # <---не используется пока нигде


class Base(DeclarativeBase):  # <---ЧЁ ЭТО?
    pass
#

app = Flask(__name__)
CORS(app)
# CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

DEBUG = 1
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
        # например, возвращение страницы с формой загрузки файла
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
@cross_origin()
def update():
    rowIndex = int(request.form.get('rowIndex'))
    colIndex = int(request.form.get('colIndex'))
    newData = request.form.get('newData')

    upd_newData, upd_colIndex = route_by_columns(rowIndex, colIndex, newData)

    # Создание ответа с обновленными данными
    response_data = {'status': 'success', 'newData': upd_newData, 'colIndex': upd_colIndex, 'rowIndex': rowIndex}

    return jsonify(response_data)


@app.route('/save', methods=['POST'])
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


def get_tnvd_code(newData, column_name):
    tnvd_df = pd.DataFrame(tnvd_names)
    # Очистка newData с помощью функции stem_porter
    cleaned_newData = stem_porter(newData)
    # Итерация по датафрейму tnvd_names и проверка совпадений
    tnvd_code = ''
    for index, row in tnvd_df.iterrows():
        # Очистка names с помощью функции stem_porter
        cleaned_name = stem_porter(row['names'])
        if cleaned_name == cleaned_newData:
            # Получаем значение 'КОД ТНВД'
            tnvd_code = tnvd_df['tnvd'][index]
            # Преобразование tnvd_code в строку для сериализации в JSON
            tnvd_code = str(tnvd_code)
            # print(f"{tnvd_df['names'][index]} => {cleaned_name} == {cleaned_newData} : {tnvd_code}")
            break
    updated_colIndex = get_colIndex_by_colName(column_name)
    return tnvd_code, updated_colIndex


def route_by_columns(rowIndex, colIndex, newData):
    """
    В зависимости от имени редактируемой колонки,
    применять определенный набор функций.
    :return: (upd_newData), (upd_colIndex)
    """
    # Получаем Имя колонки отредактированной ячейки
    col_name = get_colName_by_colIndex(colIndex)
    print(col_name)

    # Если редактировали значение в колонке 'НАИМЕНОВАНИЕ2',
    if col_name == 'НАИМЕНОВАНИЕ2':
        # то получаем 'КОД ТНВД' и индекс колонки
        upd_newData, upd_colIndex = get_tnvd_code(newData, 'КОД ТНВД')
    else:
        return newData, colIndex

    print(f'Col: {upd_colIndex} | Row: {rowIndex}')
    print(f'{upd_newData}')
    return upd_newData, upd_colIndex


def get_colIndex_by_colName(colName):
    """
    Получаем Индекс колонки по Заголовоку колонки
    :return: col_index
    """
    headers = request.form.getlist('headers[]')
    col_index = headers.index(colName)
    return col_index


def get_colName_by_colIndex(colIndex):
    """
    Получаем Заголовок колонки по Индексу колонки
    :return: col_name
    """
    headers = request.form.getlist('headers[]')
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