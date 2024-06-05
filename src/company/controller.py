import http
from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
)
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.encoders import jsonable_encoder

from src.company.models import Companies
from src.company.schema import CompanyCreate, CompanyUpdate
from src.company.service import CompanyService
from src.company import service, schema
from src.utils.db import get_db

company_router = APIRouter()


@company_router.get("/companies/",
                    response_description="Fetch all the companies",
                    status_code=http.HTTPStatus.OK,
                    )
def fetch_all_companies(db: Session = Depends(get_db)):
    service = CompanyService()
    companies = service.get_all_companies(db)
    return companies


@company_router.get("/companies/{company_id}",
                    response_description="Fetch a specific company",
                    status_code=http.HTTPStatus.OK,
                    )
def fetch_company_by_id(company_id: UUID, db: Session = Depends(get_db)):
    service = CompanyService()
    db_company = service.get_company_by_id(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.post("/company/", status_code=http.HTTPStatus.CREATED)
def create_company(db: Session = Depends(get_db), payload: CompanyCreate = Body()):
    service = CompanyService()

    req_company = CompanyCreate(
        id=payload.id,
        created_at=payload.created_at,
        updated_at=payload.updated_at,
        is_deleted=payload.is_deleted,
        display_name=payload.display_name,
        logo_url=payload.logo_url,
        star_rating=payload.star_rating,
        company_sentiment=payload.company_sentiment,
        description=payload.description,
        tags=payload.tags,
        review_count=payload.review_count,
        company_review=payload.company_review
    )

    payload_json = jsonable_encoder(req_company)
    company = service.create_company(db=db, payload=payload_json)

    return company


@company_router.patch("/companies/{company_id}",
                      status_code=http.HTTPStatus.OK,
                      )
def update_company(company_id: str, company: CompanyUpdate, db: Session = Depends(get_db)):
    service = CompanyService()

    db_company = service.update_company(
        db, company_id=company_id, company=company)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.delete("/companies/{company_id}",
                       status_code=http.HTTPStatus.OK,
                       )
def delete_companies_by_id(company_id: UUID, db: Session = Depends(get_db)):
    service = CompanyService()
    db_company = service.delete_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company
