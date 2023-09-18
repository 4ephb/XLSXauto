$(document).ready(function () {
    let $contentEditableCells = $('td[contenteditable]');

    // При клике на ячейку начинаем редактирование
    $contentEditableCells.on('click', function () {
        let $this = $(this);
        $this.data('oldValue', $this.text());
    });

    // При нажатии на Enter заканчиваем редактирование и сохраняем данные в DataFrame
    $contentEditableCells.on('keypress', function (e) {
        if (e.which === 13) {
            $(this).blur();
        }
    }).on('blur', function () {
        let $this = $(this);
        let newValue = $this.text();
        if (newValue !== $this.data('oldValue')) {
            let cellId = $(this).data('id');
            $this.data('oldValue', newValue);
            let data = $('#data-table tbody').html();

            // Отправляем обновленные данные на сервер
            $.ajax({
                type: "POST",
                url: "/update",
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    id: cellId,
                    value: newValue,
                    data: data
                }),
                success: function (result) {
                    console.log(result);
                }
            });
        }
    });
});
