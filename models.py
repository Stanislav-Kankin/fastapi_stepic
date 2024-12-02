from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True)
    organization_name = Column(String)
    employee_count = Column(Integer)
    hr_specialist_count = Column(Integer)
    documents_per_employee = Column(Integer)
    pages_per_document = Column(Float)
    turnover_percentage = Column(Float)
    average_salary = Column(Float)
    courier_delivery_cost = Column(Float)
    hr_delivery_percentage = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)
    total_paper_costs = Column(Float)
    total_logistics_costs = Column(Float)
    total_operations_costs = Column(Float)
    total_license_costs = Column(Float)


class PaperCosts(Base):
    __tablename__ = 'paper_costs'

    id = Column(Integer, primary_key=True)
    page_cost = Column(Float, default=0.9)
    printing_cost = Column(Float, default=0.8)
    storage_cost = Column(Float, default=1.77)
    rent_cost = Column(Float, default=0.07)


class LicenseCosts(Base):
    __tablename__ = 'license_costs'

    id = Column(Integer, primary_key=True)
    main_license_cost = Column(Float, default=15000)
    hr_license_cost = Column(Float, default=15000)
    employee_license_cost = Column(Float, default=700)


class TypicalOperations(Base):
    __tablename__ = 'typical_operations'

    id = Column(Integer, primary_key=True)
    time_of_printing = Column(Integer, default=2)
    time_of_signing = Column(Integer, default=4)
    time_of_archiving = Column(Integer, default=2)
