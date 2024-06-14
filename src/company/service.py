from sqlalchemy.orm import Session
from uuid import UUID
from http import HTTPStatus

from src.company.models import Companies
from src.company.schema import CompanyCreate, CompanyUpdate, CompanyJSONRequestSchema
from src.salary.services.get_all_reviews_service import ReviewService
from src.core.schema import GenericAPIResponseModel


class CompanyService:

    def find_company_by_id(self, db: Session, company_id: UUID):
        service = ReviewService()
        company_reviews = []
        
        for review in service.get_all_reviews(db=db):
            if str(review.get("company_id")) == str(company_id):
                company_reviews.append({
                    "title": review.get("title"),
                    "description": review.get("description")
                })
        
        data = db.query(Companies).filter(Companies.id == company_id).first()
        
        if not data:
            raise HTTPException(status_code=404, detail="Company not found")

        response = {
            "status": HTTPStatus.OK,
            "message": "success",
            "id": data.id,
            "created_at": data.created_at,
            "updated_at": data.updated_at,
            "is_deleted": data.is_deleted,
            "display_name": data.display_name,
            "logo_url": data.logo_url,
            "company_sentiment": data.company_sentiment,
            "review_count": len(company_reviews),
            "description": data.description,
            "star_rating": data.star_rating,  # Make sure to get the star rating from data, not review
            "tags": data.tags,
            "company_reviews": company_reviews,
        }
  
        return response

    def get_company_by_id(self, db: Session, company_id: UUID):
        return self.find_company_by_id(db=db, company_id=company_id)

    def get_all_companies(self, db: Session):
        get_all = db.query(Companies).all()
        return get_all or []

    def search_companies_by_name(self, db: Session, name: str):
        return db.query(Companies).filter(Companies.display_name.ilike(f"%{name}%")).all()

    def search_companies_by_tags(self, db: Session, name: str = None, tags: str = None):
        query = db.query(Companies)
        
        if name:
            query = query.filter(Companies.display_name.ilike(f"%{name}%"))
        
        if tags:
            tag_list = tags.split(',')
            query = query.filter(Companies.tags.overlap(tag_list))
        
        return query.all()

    def get_company_id_by_name(self, db: Session, company_name: str):
        company = db.query(Companies).filter(Companies.display_name == company_name).first()
        return company.id if company else None

    def create_company(self, db: Session, payload: dict):
        company = Companies(**payload)
        db.add(company)
        db.commit()
        db.refresh(company)
        return company

    def update_company(self, db: Session, company_id: UUID, company: CompanyUpdate):
        db_company = db.query(Companies).filter(Companies.id == company_id).first()
        if db_company:
            for key, value in company.dict(exclude_unset=True).items():
                setattr(db_company, key, value)
            db.commit()
            db.refresh(db_company)
        else:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company

    def delete_company(self, db: Session, company_id: UUID):
        db_company = db.query(Companies).filter(Companies.id == company_id).first()
        if db_company:
            db.delete(db_company)
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company
