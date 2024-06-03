from sqlalchemy.orm import Session
from uuid import UUID
from src.company.models import Companies, CompanyReview
from src.company.schema import CompanyCreate, CompanyUpdate, CompanyReviewCreate, CompanyReviewUpdate


def get_company(db: Session, company_id: UUID):
    return db.query(Companies).filter(Companies.id == company_id).first()


def get_companies(db: Session):
    return db.query(Companies).all()


def create_company(db: Session, company: CompanyCreate):
    db_company = Companies(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def update_company(db: Session, company_id: UUID, company: CompanyUpdate):
    db_company = db.query(Companies).filter(Companies.id == company_id).first()
    if db_company:
        for key, value in company.dict(exclude_unset=True).items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: UUID):
    db_company = db.query(Companies).filter(Companies.id == company_id).first()
    if db_company:
        db.delete(db_company)
        db.commit()
    return db_company
