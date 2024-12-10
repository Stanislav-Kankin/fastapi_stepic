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

    // Анимация кнопки: становится овальной, нежно голубой, выводит текст "считаем..."
    button.classList.add('loading');
    button.value = 'Считаем...';

    // Ждем 2 секунды
    setTimeout(() => {
        // Возвращаем кнопку в исходное состояние с текстом "Успех!"
        button.classList.remove('loading');
        button.classList.add('success');
        button.value = 'Успех!';

        // Запускаем анимацию конфети
        fireConfetti();

        // Ждем 1 секунду, чтобы показать текст "Успех!"
        setTimeout(() => {
            // Отправляем форму
            form.submit();
        }, 1500);
    }, 3000);
}

// Анимация конфети
function fireConfetti() {
    confetti({
        particleCount: 200, // Количество частиц
        spread: 100, // Распространение
        origin: { y: 0.6 }, // Положение взрыва (внизу)
        colors: ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff'], // Цвета конфети
    });
}