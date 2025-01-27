from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from database import init_db, get_db_session
from models import UserData, PaperCosts, LicenseCosts, TypicalOperations
from calculator import calculate_costs
from graph import generate_cost_graph
import logging


# Используем lifespan для управления событиями запуска и завершения
@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Контекстный менеджер для приложения FastAPI.

Аргументы:

app: приложение FastAPI
Описание:

Инициализирует базу данных.
Записывает в лог информацию о запуске приложения.
Выполняет логику завершения работы приложения.
Записывает в лог информацию о завершении работы приложения.
Этот контекстный менеджер используется для выполнения логики
инициализации и завершения работы приложения FastAPI.
При запуске приложения выполняется инициализация базы
данных и записывается информация о запуске приложения.
При завершении работы приложения записывается информация
о его завершении. '''
    # Логика инициализации (startup)
    init_db()
    logging.info("Application startup")
    yield
    # Логика завершения (shutdown)
    logging.info("Application shutdown")

app = FastAPI(lifespan=lifespan)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка шаблонов Jinja2
templates = Jinja2Templates(directory="templates")


# Фильтр для форматирования чисел
def format_number_filter(value):
    ''' Функция форматирования числа.

Аргументы:

value: число для форматирования
Описание: Форматирует число, добавляя пробелы между тысячами.

Возвращает отформатированное число. '''

    return "{:,.0f}".format(value).replace(",", " ")


templates.env.filters["format_number"] = format_number_filter


# Маршрут для главной страницы
@app.get("/")
async def read_root(request: Request):
    ''' Функция обработки GET-запроса к корневому URL.

Аргументы:

request: запрос пользователя
Описание: Возвращает шаблон index.html с
контекстом, содержащим запрос пользователя.

Эта функция обрабатывает GET-запросы к корневому
URL и возвращает шаблон index.html с контекстом,
содержащим запрос пользователя. '''

    return templates.TemplateResponse("index.html", {"request": request})


# Маршрут для страницы обратной связи
@app.get("/feedback")
async def read_feedback(request: Request):
    ''' Функция обработки GET-запроса к URL /feedback.

Аргументы:

request: запрос пользователя
Описание: Возвращает шаблон feedback.html с
контекстом, содержащим запрос пользователя.

Эта функция обрабатывает GET-запросы к
URL /feedback и возвращает шаблон feedback.html
с контекстом, содержащим запрос пользователя. '''

    return templates.TemplateResponse("feedback.html", {"request": request})


# Обработка отправки формы обратной связи
@app.post("/submit_feedback")
async def submit_feedback(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    organization_name: str = Form(...),
    session=Depends(get_db_session)
):
    ''' Функция обработки POST-запроса к URL /submit_feedback.

Аргументы:

request: запрос пользователя
name: имя пользователя
phone: номер телефона пользователя
email: адрес электронной почты пользователя
organization_name: название организации пользователя
session: сессия базы данных
Описание: Обрабатывает обратную связь от пользователя,
сохраняет ее в базе данных и возвращает шаблон
feedback_success.html с контекстом, содержащим запрос
пользователя. Если при обработке обратной связи возникает
ошибка, записывает информацию об ошибке в лог и
возвращает шаблон error.html с сообщением об ошибке.

Эта функция обрабатывает POST-запросы к
URL /submit_feedback, сохраняет обратную связь от пользователя
в базе данных и возвращает шаблон feedback_success.html
с контекстом, содержащим запрос пользователя. Если при
обработке обратной связи возникает ошибка, записывает
информацию об ошибке в лог и возвращает шаблон error.html
с сообщением об ошибке. '''

    try:
        # Логика обработки обратной связи
        return templates.TemplateResponse(
            "feedback_success.html", {"request": request}
            )
    except Exception as e:
        logging.error(f"Error during feedback submission: {e}")
        return templates.TemplateResponse(
            "error.html", {
                "request": request,
                "message": f"Произошла ошибка: {str(e)}"
            }
        )


# Маршрут для страницы формы
@app.get("/form")
async def read_form(request: Request):
    ''' Функция обработки GET-запроса к URL /form.

Аргументы:

request: запрос пользователя
Описание: Возвращает шаблон form.html с контекстом,
содержащим запрос пользователя.

Эта функция обрабатывает GET-запросы к
URL /form и возвращает шаблон form.html
с контекстом, содержащим запрос пользователя.
'''
    return templates.TemplateResponse("form.html", {"request": request})


# Проверка лицензии и переход к расчетам
@app.post("/check_license")
async def check_license(
    request: Request,
    organization_name: str = Form(...),
    employee_count: int = Form(...),
    hr_specialist_count: int = Form(...),
    documents_per_employee: int = Form(...),
    pages_per_document: float = Form(...),
    turnover_percentage: float = Form(...),
    average_salary: float = Form(...),
    courier_delivery_cost: float = Form(...),
    hr_delivery_percentage: float = Form(...),
):
    ''' Функция обработки POST-запроса к URL /check_license.

Аргументы:

request: запрос пользователя
organization_name: название организации
employee_count: количество сотрудников
hr_specialist_count: количество HR-специалистов
documents_per_employee: количество документов на одного сотрудника
pages_per_document: количество страниц на один документ
turnover_percentage: процент текучести
average_salary: средняя зарплата
courier_delivery_cost: стоимость курьерской доставки
hr_delivery_percentage: процент доставки HR
Описание:
Проверяет количество сотрудников и, если оно меньше или
равно 499, возвращает шаблон license.html с контекстом, содержащим
запрос пользователя и данные формы. Если количество сотрудников
больше 499, перенаправляет пользователя на URL /calculate.

Эта функция обрабатывает POST-запросы к URL /check_license, проверяет
количество сотрудников и, если оно меньше или равно 499,
возвращает шаблон license.html с контекстом, содержащим запрос
пользователя и данные формы. Если количество сотрудников больше 499,
перенаправляет пользователя на URL /calculate.
'''
    if employee_count <= 499:
        return templates.TemplateResponse(
            "license.html", {
                "request": request,
                "organization_name": organization_name,
                "employee_count": employee_count,
                "hr_specialist_count": hr_specialist_count,
                "documents_per_employee": documents_per_employee,
                "pages_per_document": pages_per_document,
                "turnover_percentage": turnover_percentage,
                "average_salary": average_salary,
                "courier_delivery_cost": courier_delivery_cost,
                "hr_delivery_percentage": hr_delivery_percentage,
            }
        )
    else:
        # Если сотрудников больше 499, сразу переходим к расчетам
        return RedirectResponse(url="/calculate", status_code=307)


# Основной маршрут для расчетов
@app.post("/calculate")
async def calculate(
    request: Request,
    organization_name: str = Form(...),
    employee_count: int = Form(...),
    hr_specialist_count: int = Form(...),
    documents_per_employee: int = Form(...),
    pages_per_document: float = Form(...),
    turnover_percentage: float = Form(...),
    average_salary: float = Form(...),
    courier_delivery_cost: float = Form(...),
    hr_delivery_percentage: float = Form(...),
    license_type: str = Form(None),  # Опционально, если сотрудников <= 499
    session=Depends(get_db_session)
):
    ''' Функция обработки POST-запроса к URL /calculate.

Аргументы:

request: запрос пользователя
organization_name: название организации
employee_count: количество сотрудников
hr_specialist_count: количество HR-специалистов
documents_per_employee: количество документов на одного сотрудника
pages_per_document: количество страниц на один документ
turnover_percentage: процент текучести
average_salary: средняя зарплата
courier_delivery_cost: стоимость курьерской доставки
hr_delivery_percentage: процент доставки HR
license_type: тип лицензии (опционально, если сотрудников <= 499)
session: сессия базы данных
Описание:
Вычисляет стоимость лицензии, получает данные из базы данных,
выполняет расчеты, генерирует график, сохраняет данные в базу
данных и возвращает шаблон result.html с контекстом, содержащим
запрос пользователя, результаты расчетов, путь к графику и
данные для отображения лицензии.

Эта функция обрабатывает POST-запросы к URL /calculate,
вычисляет стоимость лицензии, получает данные из базы данных,
выполняет расчеты, генерирует график, сохраняет данные в базу
данных и возвращает шаблон result.html с контекстом, содержащим
запрос пользователя, результаты расчетов, путь к графику и данные
для отображения лицензии. Если при обработке запроса возникает
ошибка, записывает информацию об ошибке в лог и возвращает
шаблон error.html с сообщением об ошибке.
'''
    try:
        # Определяем стоимость лицензии
        if employee_count <= 499:
            if license_type == "lite":
                employee_license_cost = 500
            elif license_type == "standard":
                employee_license_cost = 700
            else:
                employee_license_cost = 700  # По умолчанию
        elif 500 <= employee_count <= 1999:
            employee_license_cost = 700
        else:
            employee_license_cost = 600

        # Получение данных из базы данных
        paper_costs = session.query(PaperCosts).first()
        license_costs = session.query(LicenseCosts).first()
        typical_operations = session.query(TypicalOperations).first()

        if not paper_costs or not license_costs or not typical_operations:
            logging.error("Missing data in the database")
            return templates.TemplateResponse(
                "error.html", {
                    "request": request,
                    "message": "Отсутствуют данные в базе данных. Пожалуйста, свяжитесь с администратором."
                }
            )

        # Расчет стоимости
        data = {
            "organization_name": organization_name,
            "employee_count": employee_count,
            "hr_specialist_count": hr_specialist_count,
            "documents_per_employee": documents_per_employee,
            "pages_per_document": pages_per_document,
            "turnover_percentage": turnover_percentage,
            "average_salary": average_salary,
            "courier_delivery_cost": courier_delivery_cost,
            "hr_delivery_percentage": hr_delivery_percentage,
            "license_type": license_type,
            "employee_license_cost": employee_license_cost
        }

        results = calculate_costs(
            data, paper_costs, license_costs, typical_operations
        )

        # Генерация графика
        graph_path = generate_cost_graph(
            results['total_paper_costs'],
            results['total_logistics_costs'],
            results['total_operations_costs'],
            results['total_license_costs']
        )

        # Сохранение данных в базу данных
        user_data = UserData(
            organization_name=data["organization_name"],
            employee_count=data["employee_count"],
            hr_specialist_count=data["hr_specialist_count"],
            documents_per_employee=data["documents_per_employee"],
            pages_per_document=data["pages_per_document"],
            turnover_percentage=data["turnover_percentage"],
            average_salary=data["average_salary"],
            courier_delivery_cost=data["courier_delivery_cost"],
            hr_delivery_percentage=data["hr_delivery_percentage"],
            license_type=data["license_type"],
            total_paper_costs=results['total_paper_costs'],
            total_logistics_costs=results['total_logistics_costs'],
            total_operations_costs=results['total_operations_costs'],
            total_license_costs=results['total_license_costs']
        )
        session.add(user_data)
        session.commit()

        logging.info("Calculation completed successfully")

        # Возврат результатов пользователю
        return templates.TemplateResponse(
            "result.html", {
                "request": request,
                "results": results,
                "graph_path": graph_path,  # Передаем путь к графику в шаблон
                "data": data  # Передаем данные для отображения лицензии
            }
        )

    except Exception as e:
        logging.error(f"Error during calculation: {e}")
        return templates.TemplateResponse(
            "error.html", {
                "request": request,
                "message": f"Произошла ошибка: {str(e)}"
            }
        )


# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
