from sqlalchemy.orm import Session
from uuid import UUID
from http import HTTPStatus
from fastapi import HTTPException
from typing import List

from src.company.models import Companies
from src.company.schema import CompanyUpdate
from src.core.schema import GenericAPIResponseModel
from src.salary.services.get_all_reviews_service import ReviewService
from src.review.services.gcs_service import CloudStorageService


class CompanyService:

    def _get_company_reviews(self, db: Session, company_id: UUID):
        service = ReviewService()
        reviews = [
            {"title": review.get("title"), "description": review.get("description")}
            for review in service.get_all_reviews(db=db)
            if str(review.get("company_id")) == str(company_id)
        ]
        return reviews

    def _get_company_keywords(self, db: Session, input_strings: List[str], company_name: str):
        service = CloudStorageService()
        keywords = service.keyword_extractor(input_strings=input_strings, company_name=company_name)
        return keywords

    def _get_company_response(self, db: Session, company):
        company_reviews = self._get_company_reviews(db, company.id)
        input_strings = []

        for review in company_reviews:
            input_strings.append(review.get("description"))
        
        keywords = self._get_company_keywords(db, input_strings, company.display_name)
        input_strings = []

        return {
            "id": company.id,
            "created_at": company.created_at,
            "updated_at": company.updated_at,
            "is_deleted": company.is_deleted,
            "display_name": company.display_name,
            "logo_url": company.logo_url,
            "company_sentiment": company.company_sentiment,
            "review_count": len(company_reviews),
            "description": company.description,
            "star_rating": company.star_rating,
            "tags": company.tags,
            "keywords": keywords,
            "company_reviews": company_reviews,
        }

    def find_company_by_id(self, db: Session, company_id: UUID):
        company = db.query(Companies).filter(Companies.id == company_id).first()
        
        if not company:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Company not found")

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully found company by ID",
            data=self._get_company_response(db, company)
        )
        
        return response

    def get_company_by_id(self, db: Session, company_id: UUID):
        return self.find_company_by_id(db=db, company_id=company_id)

    def get_all_companies(self, db: Session):
        companies = db.query(Companies).all()
        results = [self._get_company_response(db, company) for company in companies]

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully retrieved all companies",
            data=results
        )
        return response

    def search_companies_by_name(self, db: Session, name: str):
        companies = db.query(Companies).filter(Companies.display_name.ilike(f"%{name}%")).all()
        results = [self._get_company_response(db, company) for company in companies]

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully searched companies by name",
            data=results
        )
        return response

    def search_companies_by_tags(self, db: Session, name: str = None, tags: str = None):
        query = db.query(Companies)
        
        if name:
            query = query.filter(Companies.display_name.ilike(f"%{name}%"))
        
        if tags:
            tag_list = tags.split(',')
            query = query.filter(Companies.tags.overlap(tag_list))
        
        results = [self._get_company_response(db, company) for company in query.all()]

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully searched companies by tags",
            data=results
        )
        return response
    
    def get_company_id_by_name(self, db: Session, company_name: str):
        company = db.query(Companies).filter(Companies.display_name == company_name).first()
        return company.id if company else None
    
    def update_company(self, db: Session, company_id: UUID, company: CompanyUpdate):
        db_company = db.query(Companies).filter(Companies.id == company_id).first()
        if not db_company:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Company not found")

        for var, value in vars(company).items():
            setattr(db_company, var, value) if value else None

        db.add(db_company)
        db.commit()
        db.refresh(db_company)

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully updated company",
            data=self._get_company_response(db, db_company)
        )
        return response

    def create_company(self, db: Session, payload: dict):
        company = Companies(**payload)
        db.add(company)
        db.commit()
        db.refresh(company)

        response = GenericAPIResponseModel(
            status=HTTPStatus.CREATED,
            message="Successfully created company",
            data=self._get_company_response(db, company)
        )
        return response

    def delete_company(self, db: Session, company_id: UUID):
        db_company = db.query(Companies).filter(Companies.id == company_id).first()
        if db_company:
            db.delete(db_company)
            db.commit()
        else:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Company not found")
        
        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully deleted company",
            data=None
        )
        return response
