import http
import uuid
from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from http import HTTPStatus

from src.company.models import Companies
from src.company.schema import CompanyCreate, CompanyName, CompanyUpdate, CompanyCreateRequest
from src.company.service import CompanyService
from src.core.schema import GenericAPIResponseModel
from src.company import service, schema
from src.review.services.upload_service import UploadService
from src.utils.db import get_db
from src.account.model import User
from src.account.security import get_current_user
from src.utils.time import get_datetime_now_jkt

VERSION = "v1"
ENDPOINT = "company"

company_router = APIRouter(prefix=f"/{VERSION}/{ENDPOINT}", tags=[ENDPOINT])

@company_router.get(
    "/all",
    response_description="Fetch all the companies",
    status_code=http.HTTPStatus.OK,
)
def fetch_all_companies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CompanyService()
    companies = service.get_all_companies(db)
    return companies

@company_router.get(
    "/search-name",
    response_description="Search companies by name",
    status_code=http.HTTPStatus.OK,
)
def search_company_by_name(
    name: str = Query(..., description="Name of the company to search for"), 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    service = CompanyService()
    companies = service.search_companies_by_name(db, name=name)
    return companies

@company_router.get(
    "/search-tags",
    response_description="Search companies by name or tags",
    status_code=http.HTTPStatus.OK,
)
def search_company(
    name: str = Query(None, description="Name of the company to search for"),
    tags: str = Query(None, description="Comma-separated tags to filter companies"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = CompanyService()
    companies = service.search_companies_by_tags(db, name=name, tags=tags)
    return companies

@company_router.get(
    "/{company_id}",
    response_description="Fetch a specific company",
    status_code=http.HTTPStatus.OK,
)
def fetch_company_by_id(company_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CompanyService()
    db_company = service.get_company_by_id(db=db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.post("/", status_code=http.HTTPStatus.CREATED)
def create_company(db: Session = Depends(get_db), payload: CompanyCreateRequest = Body()):
    service = CompanyService()

    time_now = get_datetime_now_jkt()

    req_company = CompanyCreate(
        id=uuid.uuid4(),
        created_at=time_now,
        updated_at=time_now,
        is_deleted=payload.is_deleted,
        display_name=payload.display_name,
        logo_url=payload.logo_url,
        star_rating=payload.star_rating,
        company_sentiment=payload.company_sentiment,
        description=payload.description,
        tags=payload.tags,
        review_count=payload.review_count,
        company_review=payload.company_review,
    )

    payload_json = jsonable_encoder(req_company)
    company = service.create_company(db=db, payload=payload_json)

    return company


@company_router.patch(
    "/{company_id}",
    status_code=http.HTTPStatus.OK,
)
def update_company(
    company_id: str, company: CompanyUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    service = CompanyService()

    db_company = service.update_company(db, company_id=company_id, company=company)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.delete(
    "/{company_id}",
    status_code=http.HTTPStatus.OK,
)
def delete_company_by_id(company_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = CompanyService()
    db_company = service.delete_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company
