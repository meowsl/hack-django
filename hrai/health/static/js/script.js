$(function () {
    $('[data-code]').mouseenter(function () {
        const title = $(this).attr('data-title');
        $('.district span').html(title);
        $('.district').show();
        $(this).addClass('hovered');
    });

    $('[data-code]').mouseleave(function () {
        if (!$('.rf-map').hasClass("open")) {
            $('.district').hide();
        }
        $(this).removeClass('hovered'); // Удаляем класс при уходе с элемента
    });

    $('[data-code]').each(function () {
        let id = $(this).attr('data-code');
        let title = $(this).attr('data-title');
        if ($('#' + id).text() != '') {
            $('.district-links').append('<div data-title="' + title + '" data-code="' + id + '">' + title + '</div>');
        }
    });
});

const myInput = document.getElementById('my-input');
const output = document.getElementById('output');
let data = [];

// Функция для загрузки данных с сервера
function loadData() {
    fetch('/api/jsonmodels/')
        .then(response => response.json())
        .then(jsonData => {
            data = jsonData;
        })
        .catch(error => {
            console.error('Ошибка загрузки данных: ', error);
        });
}

myInput.addEventListener('input', function () {
    const inputValue = myInput.value;
    if (inputValue) {
        const regions = [];
        let regionTitle = ''; // Переменная для хранения data-title

        data.forEach(item => {
            if (item.city === inputValue && !regions.includes(item.region)) {
                regions.push(item.region);
                regionTitle = item.region; // Сохраняем data-title
            }
        });

        if (regions.length > 0) {

            // Добавляем класс для изменения стиля
            $('[data-code]').removeClass('hovered'); // Сначала удаляем класс со всех элементов

            // Отображаем data-title на карте
            $('.district span').html(regionTitle);
            $('.district').show();

            regions.forEach(region => {
                $(`[data-title="${region}"]`).addClass('hovered');
            });
        } else {
            output.textContent = 'Регион не найден';
            $('.district').hide();
        }
    } else {
        output.textContent = ''; // Очищаем вывод, если поле ввода пустое
        $('[data-code]').removeClass('hovered'); // Удаляем класс при пустом поле ввода
        $('.district').hide();
    }
});


// Вызываем функцию для загрузки данных
loadData();

const loader = document.getElementById("loader");
const button = document.getElementById("btn");

button.addEventListener("click", () => {
    // Показать индикатор загрузки перед выполнением запроса
    loader.style.display = "block";

    // Выполните ваш запрос или операцию
    yourAsyncOperation()
        .then(() => {
            // Завершение успешное, скрыть индикатор загрузки
            loader.style.display = "none";
        })
        .catch(() => {
            // Завершение с ошибкой, также скрыть индикатор загрузки
            loader.style.display = "none";
        });
});

function yourAsyncOperation() {
    // Ваш запрос или операция, возвращающие Promise
    return new Promise((resolve, reject) => {
        // Ваш код запроса или операции
        // По завершении вызывайте resolve() для успешного выполнения
        // или reject() в случае ошибки
    });
}