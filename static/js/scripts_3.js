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
        // $(this).attr('contenteditable', 'false');
    }
}).on('blur', function() {
    // $(this).attr('contenteditable', 'false');
    var headers = [];
    $('th').each(function() {
        headers.push($(this).text());
    });

    var rowIndex = $(this).closest('tr').index();
    var colIndex = $(this).index();
    var cellData = $(this).data('oldValue');
    // var cellData = $(this).text($(this).data('oldValue'));
    // var cellData = $(this).text();
    var rowData = [];
    $(this).closest('tr').find('td').each(function() {
       rowData.push($(this).text());
    });

    $.ajax({
        type: 'POST',
        url: '/update',
        data: JSON.stringify({
            rowIndex: rowIndex + 1,
            colIndex: colIndex,
            cellData: cellData,
            headers: headers,
            rowData: rowData,
        }),
        contentType: 'application/json',
        success: function(response) {
            // // Обновление ячейки таблицы новыми данными
            // $('table tr').eq(rowIndex + 1).find('td').eq(response.colIndex).text(response.cellData);

            // Обновление всей строки новыми данными
            $('table tr').eq(response.rowIndex + 1).find('td').each(function(index) {
                $(this).text(response.rowData[index]);
            });

            // alert('Данные успешно обновлены!');
        }
    });
});

function bindCellEvents() {
    $('td').on('click', function() {
        // $(this).attr('contenteditable', 'true');
        $(this).data('oldValue', $(this).text());
    });

    $('td').on('keydown', function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            $(this).blur();
        } else if (event.keyCode === 27) {
            event.preventDefault();
            $(this).text($(this).data('oldValue'));
            // $(this).attr('contenteditable', 'false');
        }
    }).on('blur', function() {
        // $(this).attr('contenteditable', 'false');
        // Остальной код для отправки AJAX-запроса и обновления данных
            var headers = [];
            $('th').each(function() {
                headers.push($(this).text());
            });

            var rowIndex = $(this).closest('tr').index();
            var colIndex = $(this).index();
            var cellData = $(this).data('oldValue');
            // var cellData = $(this).text($(this).data('oldValue'));
            // var cellData = $(this).text();
            var rowData = [];
            $(this).closest('tr').find('td').each(function() {
               rowData.push($(this).text());
            });

            $.ajax({
                type: 'POST',
                url: '/update',
                data: JSON.stringify({
                    rowIndex: rowIndex + 1,
                    colIndex: colIndex,
                    cellData: cellData,
                    headers: headers,
                    rowData: rowData,
                }),
                contentType: 'application/json',
                success: function(response) {
                    // // Обновление ячейки таблицы новыми данными
                    // $('table tr').eq(rowIndex + 1).find('td').eq(response.colIndex).text(response.cellData);

                    // Обновление всей строки новыми данными
                    $('table tr').eq(response.rowIndex + 1).find('td').each(function(index) {
                        $(this).text(response.rowData[index]);
                    });

                    // alert('Данные успешно обновлены!');
                }
            });
    });
}

$('#usdBtn, #krwBtn, #jpyBtn, #cnyBtn').click(function(){
    var currency = $(this).val();
    var headers = [];
    var data = [];

    // Получение заголовков
    $('th').each(function() {
        headers.push($(this).text());
    });

    // Получение данных
    var table = $('#ResultTable').DataTable();
    table.rows().every(function () {
        var rowData = []
        $(this.node()).find('td').each(function () {
            rowData.push($(this).text());
        });
        data.push(rowData)
    });

    // // Получение данных
    // $('table tbody tr').each(function() {
    //     var rowData = [];
    //     $(this).find('td').each(function() {
    //         rowData.push($(this).text());
    //     });
    //     data.push(rowData);
    // });

    $.ajax({
        type: 'POST',
        url: '/convert_currency',
        data: {
            currency: currency,
            headers: JSON.stringify(headers),
            data: JSON.stringify(data)
        },
        success: function(response) {
            // // Обновление заголовков
            // $('th').each(function(index) {
            //     $(this).text(response.headers[index]);
            // });

            // Удаление существующих строк
            table.clear().draw();

            // Добавление обновленных данных
            response.data.forEach(function(rowData) {
                table.row.add(rowData).draw();
            });
            console.log(response);
            bindCellEvents();
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