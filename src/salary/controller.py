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
from src.salary.schema import SalaryCreate
from src.salary.service import SalaryService
from src.utils.db import get_db
from src.salary.models import Salaries

salary_router = APIRouter()


@salary_router.post("/compare-salary", status_code=http.HTTPStatus.OK)
def post_compare_salary(payload: SalaryCreate = Body()):
    service = SalaryService()

    if (
        (len(payload.roles_compare_salary) != 2)
        or (len(payload.companies_compare_salary) != 2)
        or (len(payload.locations_compare_salary) != 2)
    ):
        print("error")
    else:
        req_salary = SalaryCreate(
            id=payload.id,
            roles_compare_salary=payload.roles_compare_salary,
            companies_compare_salary=payload.companies_compare_salary,
            locations_compare_salary=payload.locations_compare_salary,
        )

        payload_json = jsonable_encoder(req_salary)
        salary = service.compare_salary(payload=payload_json)

        return salary
