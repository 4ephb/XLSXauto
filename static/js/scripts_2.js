$(document).ready(function () {
    $('#ResultTable').DataTable({
        // Задать номер строки, на которой должен быть зафиксирован заголовок
        fixedHeader: {
            header: true,
            headerOffset: 0,
        }
    });
});

$('#fileInput').change(function () {
    $('input[type="submit"]').click();
});

$('td').on('click', function() {
    $(this).attr('contenteditable', 'true');
    $(this).data('oldValue', $(this).text());
});

$('td').on('keydown', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        $(this).blur();
    } else if (event.keyCode === 27) {
        event.preventDefault();
        $(this).text($(this).data('oldValue'));
        $(this).attr('contenteditable', 'false');
    }
}).on('blur', function() {
    $(this).attr('contenteditable', 'false');
    var headers = [];
    $('th').each(function() {
        headers.push($(this).text());
    });

    var rowIndex = $(this).closest('tr').index();
    var colIndex = $(this).index();
    // var newData = $(this).data('value');
    var newData = $(this).text();

    $.ajax({
        type: 'POST',
        url: '/update',
        data: {rowIndex: rowIndex, colIndex: colIndex, newData: newData, headers: headers},
        success: function(response) {
            // Обновление ячейки таблицы новыми данными
            $('table tr').eq(rowIndex + 1).find('td').eq(response.colIndex).text(response.newData);
            // alert('Данные успешно обновлены!');
        }
    });
});

$('#saveBtn').on('click', function() {
    var data = [];
    var headers = [];

    $('th').each(function() {
        headers.push($(this).text());
    });

    var table = $('#ResultTable').DataTable();

    table.rows().every(function () {
        var rowData = []
        $(this.node()).find('td').each(function () {
            rowData.push($(this).text());
        });
        data.push(rowData)
    });

    // $('td').each(function() {
    //     data.push($(this).text());
    // });

    $.ajax({
        type: 'POST',
        url: '/save',
        // data: {data: data, headers: headers},
        data: {data: JSON.stringify(data), headers: JSON.stringify(headers)},
        // traditional: true,  // Для правильной сериализации массива
        success: function(response) {
            alert(response.message);
        }
    });
});