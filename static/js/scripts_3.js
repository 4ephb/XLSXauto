document.addEventListener('DOMContentLoaded', function () {
    // Получение данных из таблицы и отправка на сервер
    const tableData = [];

    let table = document.getElementById('ResutTable');
    let rows = table.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        let rowData = [];
        let cells = rows[i].getElementsByTagName('td');

        for (let j = 0; j < cells.length; j++) {
            rowData.push(cells[j].innerText);
        }

        tableData.push(rowData);
    }

    fetch('/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'data': tableData})
    })
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        console.log(data);
    })
    .catch(function (error) {
        console.error(error);
    });
});
