# main.py
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import init_db, get_db_session
from models import UserData, PaperCosts, LicenseCosts, TypicalOperations
from calculator import calculate_costs
from telegram_bot import send_telegram_message, format_number

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка логирования в файл
file_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def format_number_filter(value):
    return "{:,.0f}".format(value).replace(",", " ")


templates.env.filters["format_number"] = format_number_filter


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/form")
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.get("/feedback")
async def read_feedback(request: Request):
    return templates.TemplateResponse("feedback.html", {"request": request})


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
    session=Depends(get_db_session)
):
    logger.info("Received calculation request")
    logger.debug(f"Data: {locals()}")

    try:
        paper_costs = session.query(PaperCosts).first()
        license_costs = session.query(LicenseCosts).first()
        typical_operations = session.query(TypicalOperations).first()

        if not paper_costs or not license_costs or not typical_operations:
            logger.error("Missing data in the database")
            return templates.TemplateResponse(
                "error.html", {
                    "request": request,
                    "message": "Missing data in the database"
                    }
                    )

        data = {
            "organization_name": organization_name,
            "employee_count": employee_count,
            "hr_specialist_count": hr_specialist_count,
            "documents_per_employee": documents_per_employee,
            "pages_per_document": pages_per_document,
            "turnover_percentage": turnover_percentage,
            "average_salary": average_salary,
            "courier_delivery_cost": courier_delivery_cost,
            "hr_delivery_percentage": hr_delivery_percentage
        }

        results = calculate_costs(
            data, paper_costs, license_costs, typical_operations
        )

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
            total_paper_costs=results['total_paper_costs'],
            total_logistics_costs=results['total_logistics_costs'],
            total_operations_costs=results['total_operations_costs'],
            total_license_costs=results['total_license_costs']
        )
        session.add(user_data)
        session.commit()

        logger.info("Calculation completed successfully")
        return templates.TemplateResponse(
            "result.html", {
                "request": request, "results": results})

    except Exception as e:
        logger.error(f"Error during calculation: {e}")
        return templates.TemplateResponse(
            "error.html", {
                "request": request, "message": str(e)})


@app.post("/submit_feedback")
async def submit_feedback(
    request: Request,
    inn: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    preferred_contact: str = Form(...),
    session=Depends(get_db_session)
):
    logger.info("Received feedback submission")
    logger.debug(f"Data: {locals()}")

    try:
        # Получение последних результатов расчета
        last_user_data = session.query(UserData).order_by(UserData.id.desc()).first()

        if not last_user_data:
            logger.error("No calculation results found")
            return templates.TemplateResponse(
                "error.html", {
                    "request": request,
                    "message": "No calculation results found"
                    }
                    )

        # Формирование сообщения для Telegram
        message = (
            f"*Новая обратная связь:*\n\n"
            f"*ИНН:* {inn}\n"
            f"*Имя:* {name}\n"
            f"*Телефон:* {phone}\n"
            f"*Email:* {email}\n"
            f"*Предпочтительный способ связи:* {preferred_contact}\n\n"
            f"*Ранее введенные данные:*\n"
            f"*Название организации:* {last_user_data.organization_name}\n"
            f"*Число сотрудников:* {last_user_data.employee_count}\n"
            f"*Число кадровых специалистов:* {
                last_user_data.hr_specialist_count}\n"
            f"*Документов в год на сотрудника:* {
                last_user_data.documents_per_employee}\n"
            f"*Страниц в документе:* {last_user_data.pages_per_document}\n"
            f"*Текучка в процентах:* {last_user_data.turnover_percentage}\n"
            f"*Средняя зарплата:* {
                format_number(last_user_data.average_salary)}\n"
            f"*Стоимость курьерской доставки:* {format_number(
                last_user_data.courier_delivery_cost)}\n"
            f"*Процент отправки кадровых документов:* {
                last_user_data.hr_delivery_percentage}\n\n"
            f"*Результаты расчета:*\n"
            f"*Распечатывание, хранение документов:* {format_number(
                last_user_data.total_paper_costs)} руб.\n"
            f"*Расходы на доставку документов:* {format_number(
                last_user_data.total_logistics_costs)} руб.\n"
            f"*Расходы на оплату времени по работе с документами:* {
                format_number(last_user_data.total_operations_costs)} руб.\n"
            f"*Итого расходы при КДП на бумаге:* {
                format_number(
                    last_user_data.total_paper_costs +
                    last_user_data.total_logistics_costs +
                    last_user_data.total_operations_costs)} руб.\n"
            f"*Сумма КЭДО от HRlink:* {format_number(
                last_user_data.total_license_costs)} руб.\n"
            f"*Сумма выгоды:* {format_number(
                last_user_data.total_paper_costs +
                last_user_data.total_logistics_costs +
                last_user_data.total_operations_costs -
                last_user_data.total_license_costs)} руб."
        )

        # Отправка сообщения через Telegram
        send_telegram_message(message, last_user_data)

        logger.info("Feedback submitted successfully")
        return templates.TemplateResponse(
            "feedback_succsess.html", {"request": request}
            )

    except Exception as e:
        logger.error(f"Error during feedback submission: {e}")
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": str(e)}
            )
