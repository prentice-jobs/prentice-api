import http

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from src.company import service, schema
from src.utils.db import get_db

company_router = APIRouter()


@company_router.get("/companies/",
                    response_description="Fetch all the companies",
                    status_code=http.HTTPStatus.OK,
                    response_model=List[schema.Company])
def read_companies(db: Session = Depends(get_db)):
    companies = service.get_companies(db)
    return companies


@company_router.get("/companies/{company_id}",
                    response_description="Fetch a specific company",
                    status_code=http.HTTPStatus.OK,
                    response_model=schema.Company)
def read_company(company_id: UUID, db: Session = Depends(get_db)):
    db_company = service.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.post("/company/",
                     status_code=http.HTTPStatus.CREATED,
                     response_model=schema.Company)
def create_company(company: schema.CompanyCreate, db: Session = Depends(get_db)):
    return service.create_company(db=db, company=company)


@company_router.patch("/companies/{company_id}",
                      status_code=http.HTTPStatus.OK,
                      response_model=schema.Company)
def update_company(company_id: UUID, company: schema.CompanyUpdate, db: Session = Depends(get_db)):
    db_company = service.update_company(
        db, company_id=company_id, company=company)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@company_router.delete("/companies/{company_id}",
                       status_code=http.HTTPStatus.OK,
                       response_model=schema.Company)
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    db_company = service.delete_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


# import os
# from datetime import datetime
# import http

# from fastapi import (
#     APIRouter,
#     Request,
#     Response,
#     Depends,
#     Body,
#     HTTPException,
#     status
# )
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy.orm import Session
# from decouple import config
# from supabase import create_client, Client

# from . import service, schema
# from .schema import CompanyCreateSchema
# from src.utils.database import engine, SessionLocal
# from .model import Company
# import models


# company_router = APIRouter()

# models.Base.metadata.create_all(bind=engine))
# url = config("SUPABASE_URL")
# key = config("SUPABASE_KEY")

# supabase: Client = create_client(url, key)


# @company_router.post("/company/",
#                      response_description="Create a new company",
#                      status_code=http.HTTPStatus.OK,
#                      response_model=CompanyCreateSchema)
# def create_company(
#     request: Request,
#     payload: CompanyCreateSchema = Body(),
# ):
#     payload = jsonable_encoder(payload)
#     print("payload...")
#     print(payload)

#     result = supabase.table("company").insert(payload).execute()
#     print("result...")
#     print(result)

#     # if result.status_code != 201:
#     #     raise HTTPException(status_code=500, detail="Error creating company")

#     return JSONResponse(
#         status_code=http.HTTPStatus.CREATED,
#         content=result.data[0]
#     )


# @company_router.get("/companies/", response_description="Fetch all the companies",  status_code=http.HTTPStatus.OK)
# def fetch_all_companies(session: Session = Depends(get_db)):
#     companies = session.query(Company).all()
#     return companies
    # print(companies)
    # return jsonable_encoder(companies)

    # companies = supabase.table("company").select("*").execute()
    # return companies


# @company_router.get("/companies/{company_id}",
#                     response_description="Fetch a specific company",
#                     status_code=http.HTTPStatus.OK,
#                     )
# def get_company(id: str):
#     company = supabase.table("company").select("*").eq("id", id).execute()
#     return JSONResponse(
#         status_code=http.HTTPStatus.CREATED,
#         content=company
#     )


# @company_router.patch("/companies/{company_id}",
#                       response_description="Update specified fields of a company",
#                       status_code=http.HTTPStatus.OK,
#                       )
# def update_company(id: str, request: Request, payload: CompanyCreateSchema = Body()):
#     payload = jsonable_encoder(payload)
#     result = supabase.table("company").update(
#         payload).eq("id", id).execute()
#     # if result.status_code != 200:
#     #     raise HTTPException(status_code=500, detail="Error updating company")

#     return JSONResponse(
#         status_code=http.HTTPStatus.OK,
#         content=result.data[0]
#     )


# @company_router.delete("/companies/{company_id}", status_code=http.HTTPStatus.OK)
# def delete_company(id: str):
#     company = supabase.table("company").delete().eq("id", id).execute()
#     return {"message": "Company deleted successfully"}
