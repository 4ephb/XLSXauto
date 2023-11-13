// const fileInput = document.getElementById('fileInput');
// fileInput.addEventListener('change', function () {
//     this.form.submit();
// });

$('#fileInput').change(function () {
    $('input[type="submit"]').click();
});

// const headers = {{ headers|tojson }};
// const data = {{ data|tojson }};

// const headers = JSON.parse(container.getAttribute('data-headers'));
// const data = JSON.parse(container.getAttribute('data-data'));

// const parsedHeaders = JSON.parse('{{ headers|tojson|safe }}');
// const parsedData = JSON.parse('{{ data|tojson|safe }}');

const flaskHeaders = JSON.parse('{{ headers|tojson|safe }}');
const flaskData = JSON.parse('{{ data|tojson|safe }}');
console.log(flaskHeaders)
console.log(flaskData)

// const parsedHeaders = JSON.parse(headers);
// const parsedData = JSON.parse(data);



const container = document.getElementById('excel-container');
const hot = new Handsontable(container, {
    data: flaskData,
    colHeaders: flaskHeaders,
    language: 'ru-RU',
    rowHeaders: true,
    filters: true,
    search: true,
    comments: true,
    licenseKey: 'non-commercial-and-evaluation',
    contextMenu: true,
    dropdownMenu: true,
    multiColumnSorting: {
      sortEmptyCells: true,
      indicator: true,
      headerAction: true,
    },
    manualRowMove: true,
    manualColumnMove: true,
    autoColumnSize: {
        // keep 40% of columns in sync (the rest of columns: async)
        syncLimit: '100%',
        // when calculating column widths, use column headers
        useHeaders: true,
        // when calculating column widths, use 10 samples of the same length
        samplingRatio: 0,
        // when calculating column widths, allow duplicate samples
        allowSampleDuplicates: true
    },
    dragToScroll: true,
    manualColumnResize: true,
    persistentState: true,
    columns: [
        { type: 'text' }, // НАИМЕНОВАНИЕ1
        { type: 'text' }, // НАИМЕНОВАНИЕ2
        { type: 'text' }, // ИЗГОТОВИТЕЛЬ
        { type: 'text' }, // ТМ
        { type: 'text' }, // МАРКА
        { type: 'text' }, // МОДЕЛЬ
        { type: 'text' }, // АРТ
        { type: 'text' }, // СПТ
        { type: 'numeric' }, // КОЛ-ВО
        { type: 'numeric' }, // КОД
        { type: 'text' }, // НАИМ
        { type: 'numeric' }, // КОД ТНВД
        { type: 'numeric' }, // ДОП КОД
        { type: 'numeric' }, // ВЕС ШТ
        {
          // $/ШТ
          type: 'numeric',
          numericFormat: {
            pattern: '0,0.00',
            culture: 'en-US',
          },
        },
        { type: 'numeric' }, // БР
        { type: 'numeric' }, // НТ
        {
          // $/КГ
          type: 'numeric',
          numericFormat: {
            pattern: '0,0.00',
            culture: 'en-US',
          },
        },
        {
          // ЦЕНА
          type: 'numeric',
          numericFormat: {
            pattern: '0,0.00',
            culture: 'ru-RU'
          },
        },
        { type: 'text' }, // МЕСТА
        { type: 'text' }, // МЕСТ ЧАСТ
        { type: 'numeric' }, // ЕСТЬ/НЕТ
        { type: 'text' }, // КОД УП
        { type: 'text' }, // ДОП КОД УП
        { type: 'text' }, // КОД №1
        { type: 'text' }, // СЕРТ №1
        {
          // НАЧАЛО №1
          type: 'date',
          dateFormat: 'DD.MM.YYYY',
          correctFormat: true,
          defaultDate: '01.01.1900',
          datePickerConfig: {
            // First day of the week (0: Sunday, 1: Monday, etc)
            firstDay: 1,
            showWeekNumber: true,
            disableDayFn(date) {
              // Disable Sunday and Saturday
              return date.getDay() === 0 || date.getDay() === 6;
            }
          }
        },
        {
          // КОНЕЦ №1
          type: 'date',
          dateFormat: 'DD.MM.YYYY',
          correctFormat: true,
          defaultDate: '01.01.1900',
          datePickerConfig: {
            // First day of the week (0: Sunday, 1: Monday, etc)
            firstDay: 1,
            showWeekNumber: true,
            disableDayFn(date) {
              // Disable Sunday and Saturday
              return date.getDay() === 0 || date.getDay() === 6;
            }
          }
        },
        { type: 'text' }, // КОД №2
        { type: 'text' }, // СЕРТ №2
        {
          // НАЧАЛО №2
          type: 'date',
          dateFormat: 'DD.MM.YYYY',
          correctFormat: true,
          defaultDate: '01.01.1900',
          datePickerConfig: {
            // First day of the week (0: Sunday, 1: Monday, etc)
            firstDay: 1,
            showWeekNumber: true,
            disableDayFn(date) {
              // Disable Sunday and Saturday
              return date.getDay() === 0 || date.getDay() === 6;
            }
          }
        },
        {
          // КОНЕЦ №2
          type: 'date',
          dateFormat: 'DD.MM.YYYY',
          correctFormat: true,
          defaultDate: '01.01.1900',
          datePickerConfig: {
            // First day of the week (0: Sunday, 1: Monday, etc)
            firstDay: 1,
            showWeekNumber: true,
            disableDayFn(date) {
              // Disable Sunday and Saturday
              return date.getDay() === 0 || date.getDay() === 6;
            }
          }
        },
      ]
});

hot.addHook('afterChange', (changes, source) => {
    if (source === 'edit') {
        const rowIndex = changes[0][0];
        const colIndex = changes[0][1];
        const newValue = changes[0][3];

        const requestData = {
            rowIndex: rowIndex,
            colIndex: colIndex,
            cellData: newValue,
            rowData: hot.getData()[rowIndex],
            headers: flaskHeaders
        };

        fetch('/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            const updatedRowData = data.rowData;
            hot.setDataAtRowProp(rowIndex, 'rowData', updatedRowData);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

const searchField = document.querySelector('#search_field');
searchField.addEventListener('keyup', function(event) {
    // get the `Search` plugin's instance
    const search = hot.getPlugin('search');
    // use the `Search` plugin's `query()` method
    const queryResult = search.query(event.target.value);
    console.log(queryResult);
    hot.render();
});

document.getElementById('save-button').addEventListener('click', () => {
    const exportData = hot.getData();
    const exportHeaders = hot.getColHeader();

    const formData = new FormData();
    formData.append('data', JSON.stringify(exportData));
    formData.append('headers', JSON.stringify(exportHeaders));

    fetch('/download', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});