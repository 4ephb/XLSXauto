from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd

# import openpyxl as op

app = Flask(__name__)

# Переменные с заголовками таблицы
result_columns = [
    'НАИМЕНОВАНИЕ1', 'НАИМЕНОВАНИЕ2', 'ИЗГОТОВИТЕЛЬ', 'ТМ', 'МАРКА', 'МОДЕЛЬ',
    'АРТ', 'СПТ', 'КОЛ-ВО', 'КОД', 'НАИМ', 'КОД ТНВД', 'ДОП КОД', 'ВЕС ШТ',
    'БР', 'НТ', '$/КГ', 'ЦЕНА', 'МЕСТА', 'МЕСТ ЧАСТ', 'ЕСТЬ/НЕТ', 'КОД УП',
    'ДОП КОД УП', 'КОД №1', 'СЕРТ №1', 'НАЧАЛО №1', 'КОНЕЦ №1', 'КОД №2',
    'СЕРТ №2', 'НАЧАЛО №2', 'КОНЕЦ №2'
]

data = pd.DataFrame(columns=result_columns)


def update_data(dataframe, incoming_data):
    """
    Функция для обновления данных в DataFrame
    :param dataframe:
    :param incoming_data:
    :return:
    """
    global data
    updated_dataframe = pd.read_html(incoming_data)[0]
    updated_dataframe.columns = [result_columns]
    # dataframe.update(updated_dataframe)
    data = pd.concat([data, updated_dataframe], ignore_index=True, sort=False)
    return data


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


@app.route('/', methods=['GET', 'POST'])
def index():
    global data
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Чтение данных из загруженного файла xlsx
                excel_data = pd.read_excel(file)
                # Отображение только необходимых столбцов
                excel_data = excel_data[['Наименование', 'Торговая Марка', 'Количество, шт.', 'Вес БРУТТО, кг.']]
                # Переименование столбцов
                excel_data.columns = ['НАИМЕНОВАНИЕ2', 'ТМ', 'КОЛ-ВО', 'БР']
                # Добавление данных в общую таблицу
                # data = data.append(excel_data, ignore_index=True)
                data = pd.concat([data, excel_data], ignore_index=True)

    # Замена значений пустых ячеек с NaN на ''
    data = data.fillna('')

    # Применение функций чистки к столбцам
    data['НАИМЕНОВАНИЕ2'].apply(clean_1)
    data['ТМ'].apply(clean_2)

    return render_template('index.html', data=data)


@app.route('/update', methods=['POST'])
def update():
    global data
    incoming = request.get_json()['data']
    data = update_data(data, incoming)  # Обновляем данные в DataFrame
    return jsonify({'status': 'OK'})


@app.route('/save', methods=['POST'])
def save():
    """
    Сохранение данных в Excel файл и
    Очистка рабочего датафрейма data
    :return:
    """
    global data
    data.to_excel('Result.xlsx', index=False)
    # data = pd.DataFrame(columns=result_columns)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
