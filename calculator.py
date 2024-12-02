# calculator.py
from sqlalchemy.orm import sessionmaker
from models import PaperCosts, TypicalOperations
from database import engine

Session = sessionmaker(bind=engine)


def calculate_documents_per_year(data):
    employee_count = data['employee_count']
    documents_per_employee = data['documents_per_employee']
    turnover_percentage = data['turnover_percentage']
    return employee_count * (
        documents_per_employee * (
            1 + turnover_percentage / 100))


def calculate_pages_per_year(data):
    documents_per_year = calculate_documents_per_year(data)
    pages_per_document = data['pages_per_document']
    return documents_per_year * pages_per_document


def calculate_total_paper_costs(pages_per_year):
    session = Session()
    paper_costs = session.query(PaperCosts).first()
    session.close()
    return pages_per_year * (
        paper_costs.page_cost + paper_costs.printing_cost +
        paper_costs.storage_cost + paper_costs.rent_cost
    )


def calculate_total_logistics_costs(data, documents_per_year):
    courier_delivery_cost = data['courier_delivery_cost']
    hr_delivery_percentage = data.get('hr_delivery_percentage')
    return courier_delivery_cost * (
        hr_delivery_percentage / 100 * documents_per_year)


def calculate_cost_per_minute(data):
    average_salary = data['average_salary']
    working_minutes_per_month = data.get('working_minutes_per_month', 10080)
    return average_salary / working_minutes_per_month


def calculate_total_operations_costs(
        data, documents_per_year, cost_per_minute):
    session = Session()
    typical_operations = session.query(TypicalOperations).first()
    session.close()

    if not typical_operations:
        raise ValueError("Нет данных.")

    time_of_printing = typical_operations.time_of_printing
    time_of_signing = typical_operations.time_of_signing
    time_of_archiving = typical_operations.time_of_archiving

    total_operations_costs = (
        (time_of_printing * cost_per_minute) +
        (time_of_archiving * cost_per_minute) +
        (time_of_signing * cost_per_minute)
    ) * documents_per_year

    return total_operations_costs


def calculate_total_license_costs(data, license_costs):
    hr_specialist_count = data['hr_specialist_count']
    employee_count = data['employee_count']
    return (
        license_costs.hr_license_cost * hr_specialist_count +
        license_costs.employee_license_cost * employee_count +
        license_costs.main_license_cost
    )


def calculate_costs(data, paper_costs, license_costs, typical_operations):
    documents_per_year = calculate_documents_per_year(data)
    pages_per_year = calculate_pages_per_year(data)
    total_paper_costs = calculate_total_paper_costs(pages_per_year)
    total_logistics_costs = calculate_total_logistics_costs(
        data, documents_per_year)
    cost_per_minute = calculate_cost_per_minute(data)
    total_operations_costs = calculate_total_operations_costs(
        data, documents_per_year, cost_per_minute)
    total_license_costs = calculate_total_license_costs(data, license_costs)

    return {
        "total_paper_costs": total_paper_costs,
        "total_logistics_costs": total_logistics_costs,
        "total_operations_costs": total_operations_costs,
        "total_license_costs": total_license_costs
    }
