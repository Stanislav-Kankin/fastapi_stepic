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
        // Если все поля заполнены, отправляем форму
        event.target.submit();
    }
});