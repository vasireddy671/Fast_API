from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

#SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DBPlace(Base):
    __tablename__ = 'employees'

    emp_id = Column(Integer, primary_key=True, index=True)
    emp_name = Column(String(50))


Base.metadata.create_all(bind=engine)

class Place(BaseModel):
    emp_id: int
    emp_name: str


    class Config:
        orm_mode = True
def get_employee(db: Session, employee_id: int):
    return db.query(DBPlace).where(DBPlace.id == employee_id).first()

def get_employees(db: Session):
    return db.query(DBPlace).all()

def create_employee(db: Session, employee: Place):
    db_employee = DBPlace(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return db_employee

@app.post('/employees/', response_model=Place)
def create_employees_view(employee: Place, db: Session = Depends(get_db)):
    db_employee = create_employee(db, employee)
    return db_employee

@app.get('/employees/', response_model=List[Place])
def get_employees_view(db: Session = Depends(get_db)):
    return get_employees(db)

@app.get('/employee/{employee_id}')
def get_employee_view(employee_id: int, db: Session = Depends(get_db)):
    return get_employee(db, employee_id)

@app.get('/')
async def root():
    return {'message': 'Hello World!'}