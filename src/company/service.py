from sqlalchemy.orm import Session
from . import model, schema


def get_company(db: Session, company_id: int):
    return db.query(model.Company).filter(model.Company.id == company_id).first()


def get_companies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(model.Company).offset(skip).limit(limit).all()


def create_company(db: Session, company: schema.CompanyCreate):
    tags = ",".join(company.tags)  # Convert list of tags to a comma-separated string
    db_company = model.Company(**company.dict(), tags=tags)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def update_company(db: Session, company_id: int, company: schema.CompanyUpdate):
    db_company = get_company(db, company_id)
    if db_company:
        for key, value in company.dict().items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int):
    db_company = get_company(db, company_id)
    if db_company:
        db.delete(db_company)
        db.commit()
    return db_company
