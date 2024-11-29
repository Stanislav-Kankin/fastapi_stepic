# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, PaperCosts, LicenseCosts, TypicalOperations

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Проверяем, существуют ли данные в таблице PaperCosts
    if not session.query(PaperCosts).first():
        paper_costs = PaperCosts()
        session.add(paper_costs)

    # Проверяем, существуют ли данные в таблице LicenseCosts
    if not session.query(LicenseCosts).first():
        license_costs = LicenseCosts()
        session.add(license_costs)

    # Проверяем, существуют ли данные в таблице TypicalOperations
    if not session.query(TypicalOperations).first():
        typical_operations = TypicalOperations()
        session.add(typical_operations)

    session.commit()
    session.close()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
