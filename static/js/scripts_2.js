<!-- JavaScript для автоматической отправки формы -->

$(document).ready(function () {
    let $contentEditableCells = $('td[contenteditable]');

    $('#fileInput').change(function () {
        // Симулируем нажатие на кнопку "Загрузить" при выборе файла
        $('input[type="submit"]').click();
    });

    // При клике на ячейку начинаем редактирование
    $contentEditableCells.on('click', function () {
        $(this).data('oldValue', $(this).text());
    });

    // При нажатии на Enter заканчиваем редактирование и сохраняем данные в DataFrame
    $contentEditableCells.on('keypress', function (e) {
        if (e.which === 13) {
            $(this).blur();
        }
    }).on('blur', function () {
        let newValue = $(this).text();
        if (newValue !== $(this).data('oldValue')) {
            // var columnIndex = $(this).index();
            // var rowIndex = $(this).closest('tr').index() - 1;
            let cellId = $(this).data('data-id');
            $(this).data('oldValue', newValue);
            let data = $('#data-table tbody').html();
            // $('#data-table').find('tr:eq(' + (rowIndex + 2) + ')').find('td:eq(' + columnIndex + ')').text(newValue);

            // Отправляем обновленные данные на сервер
            $.ajax({
                type: "POST",
                url: "/update",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({data: data}),
               // data: JSON.stringify({
                //    id: cellId,
                //    value: newValue,
                //    data: data}),
                success: function (result) {
                    console.log(result);
                }
            });
        }
    });
});
