from sqlalchemy.orm import Session
from uuid import UUID

from src.company.models import Companies
from src.company.schema import CompanyCreate, CompanyUpdate, CompanyJSONRequestSchema


class CompanyService:
    def get_company_by_id(self, db: Session, company_id: UUID):
        return db.query(Companies).filter(Companies.id == company_id).first()

    def get_all_companies(self, db: Session):
        get_all = db.query(Companies).all()
        return get_all or None

    def create_company(self, db: Session, payload: dict):
        company = Companies(**payload)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def update_company(self, db: Session, company_id: UUID, company: CompanyUpdate):
        db_company = db.query(Companies).filter(
            Companies.id == company_id).first()
        if db_company:
            for key, value in company.dict(exclude_unset=True).items():
                setattr(db_company, key, value)
            db.commit()
            db.refresh(db_company)
        return db_company

    def delete_company(self, db: Session, company_id: UUID):
        db_company = db.query(Companies).filter(
            Companies.id == company_id).first()
        if db_company:
            db.delete(db_company)
            db.commit()
        return db_company
