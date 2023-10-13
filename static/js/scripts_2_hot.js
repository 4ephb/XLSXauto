$(document).ready(function () {
    var headers = {{ headers|tojson }};
    var data = {{ data|tojson }};

    var hot = new Handsontable(document.getElementById('ResultTable'), {
        data: data,
        colHeaders: headers,
        rowHeaders: true,
        contextMenu: true,
        dropdownMenu: true,
        stretchH: 'all',
        autoWrapRow: true,
        height: 'auto',
        afterChange: function (changes, source) {
            if (source === 'edit') {
                // Handle the change event
                // You can access the changed cell data using `hot.getDataAtCell(row, col)`
            }
        },
    });

    $('#fileInput').change(function () {
        $('input[type="submit"]').click();
    });

    $('#saveBtn').on('click', function () {
        var updatedData = hot.getData();
        var headers = hot.getColHeader();

        $.ajax({
            type: 'POST',
            url: '/save',
            data: JSON.stringify({ data: updatedData, headers: headers }),
            contentType: 'application/json',
            success: function (response) {
                alert(response.message);
            },
        });
    });
});