// Проверка заполнения полей формы
document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault(); // Предотвращаем отправку формы

    // Проверяем, что все поля заполнены
    const fields = document.querySelectorAll('input[type="text"], input[type="number"]');
    let isValid = true;

    fields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error'); // Добавляем класс для выделения ошибки
        } else {
            field.classList.remove('error'); // Убираем класс, если поле заполнено
        }
    });

    if (!isValid) {
        alert('Пожалуйста, заполните все поля корректно.');
    } else {
        // Если все поля заполнены, запускаем анимацию кнопки
        animateButton(event.target);
    }
});

// Анимация кнопки "Рассчитать"
function animateButton(form) {
    const button = form.querySelector('.calculate-button');

    // Анимация кнопки: становится круглой, нежно голубой, пульсирует
    button.classList.add('loading');
    button.querySelector('.loading-icon').textContent = '?'; // Знак вопроса

    // Ждем 3 секунды (время выполнения расчетов)
    setTimeout(() => {
        // Анимация успеха: зеленый круг с галочкой
        button.classList.remove('loading');
        button.classList.add('success');
        button.querySelector('.loading-icon').textContent = '✔'; // Галочка

        // Ждем 1 секунду, чтобы показать галочку
        setTimeout(() => {
            // Отправляем форму
            form.submit();
        }, 1000);
    }, 3000);
}