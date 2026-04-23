import os
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lab.db")

engine = create_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    expiration_date = Column(Date, nullable=False)

SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)