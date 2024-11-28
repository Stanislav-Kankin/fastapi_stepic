import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import init_db, get_db_session
from models import UserData, PaperCosts, LicenseCosts, TypicalOperations
from calculator import calculate_costs

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка логирования в файл
file_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    session = Depends(get_db_session)
):
    logger.info("Received calculation request")
    logger.debug(f"Data: {locals()}")

    paper_costs = session.query(PaperCosts).first()
    license_costs = session.query(LicenseCosts).first()
    typical_operations = session.query(TypicalOperations).first()

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

    results = calculate_costs(data, paper_costs, license_costs, typical_operations)

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
    return templates.TemplateResponse("result.html", {"request": request, "results": results})
