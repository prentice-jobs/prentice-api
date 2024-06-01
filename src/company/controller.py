# from fastapi import (
#   APIRouter,
#   Request,
#   Response,
#   Depends,
#   Body
# )

# from enum import Enum

# VERSION = "v1"
# ENDPOINT = "company"

# company_router = APIRouter(
#   prefix=f"/{VERSION}/{ENDPOINT}",
#   tags=[ENDPOINT]
# )

# # quests
# # upload company profile ngga p

# @company_router.post("")
# async def upload_company_profile(
#     # file: UploadFile = File(...)
# ):
#     service = UploadService(AWS_BUCKET_NAME)

#     # user berdasarkan id
#     # user_id = user.id

#     file_name = f"{user_id}_{sha()}_{file.filename}"
#     try:
#         service.upload_file(file, file_name)
#     # except ValueError as e:
#     #     return HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
#     # except Exception as e:
#     #     return HTTPException(status_code=500, detail="Error on uploading the file")
#     # return {"status_code": HTTP_200_OK, "filename": file_name}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import service, schema
from .database import get_db

company_router = APIRouter()


@company_router.post("/companies/", response_model=schema.Company)
def create_company(company: schema.CompanyCreate, db: Session = Depends(get_db)):
    return service.create_company(db=db, company=company)


@company_router.get("/companies/{company_id}", response_model=schema.Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = service.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.get("/companies/", response_model=list[schema.Company])
def read_companies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    companies = service.get_companies(db, skip=skip, limit=limit)
    return companies


@company_router.put("/companies/{company_id}", response_model=schema.Company)
def update_company(
    company_id: int, company: schema.CompanyUpdate, db: Session = Depends(get_db)
):
    return service.update_company(db=db, company_id=company_id, company=company)


@company_router.delete("/companies/{company_id}", response_model=schema.Company)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    return service.delete_company(db=db, company_id=company_id)
