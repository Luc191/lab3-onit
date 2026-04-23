from datetime import date
from sqlalchemy import select

from db import Base, Product, SessionLocal, engine

def test_create_and_read_product():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        product = Product(
            name="Milk",
            weight=1000,
            expiration_date=date(2026, 5, 1)
        )
        session.add(product)
        session.commit()

    with SessionLocal() as session:
        found = session.scalars(
            select(Product).where(Product.name == "Milk")
        ).first()

    assert found is not None
    assert found.weight == 1000
    assert found.expiration_date == date(2026, 5, 1)