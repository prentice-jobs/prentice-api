import http
from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
)
from http import HTTPStatus
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from src.account.exceptions import UnauthorizedOperationException
from src.company.models import Companies
from src.core.schema import GenericAPIResponseModel
from src.review.exceptions import CreateCompanyReviewFailedException
from src.salary.schema import SalaryCreate
from src.salary.services.compare_salary_service import SalaryService
from src.utils.db import get_db
from src.salary.models import Salaries
from src.utils.response_builder import build_api_response
from prentice_logger import logger
from src.account.security import get_current_user
from src.account.model import User
from src.salary.exception import (
    CompareCompaniesSalariesFailedException,
    CompareMoreThanTwoValuesFailedException
)

VERSION = "v1"
ENDPOINT = "compare"

salary_router = APIRouter(prefix=f"/{VERSION}/{ENDPOINT}", tags=[ENDPOINT])

roles = ["Software Engineer Intern", "Quality Assurance Intern",
         'Business Development Intern', "Data Scientist Intern",
         "Product Manager Intern", "UI/UX Designer Intern",
         'Business Analyst Intern', 'Data Analyst Intern']

industries = ['Startup', 'BUMN', 'Finance', 'FMCG', 'Government',
              'Electronics', 'Healthcare', 'FnB', 'Creative and Media',
              'Professional Services']

locations = ["Banda Aceh", "Padang", "Pekanbaru",
             "Jambi", "Palembang", "Jakarta", "Depok",
             "Surabaya", "Bandung", "Semarang", "Denpasar",
             "Medan", "Yogyakarta", "Pontianak", "Palangka Raya",
             "Samarinda"]

@salary_router.get("/roles", response_model=GenericAPIResponseModel)
def get_roles():
    response = GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully get list of Roles",
                data=jsonable_encoder(roles),
            )
    return response

@salary_router.get("/industries", response_model=GenericAPIResponseModel)
def get_industries():
    response = GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully get list of Industries",
                data=jsonable_encoder(industries),
            )
    return response

@salary_router.get("/locations", response_model=GenericAPIResponseModel)
def get_locations():
    response = GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully get list of Locations",
                data=jsonable_encoder(locations),
            )
    return response


@salary_router.post("/salary", status_code=http.HTTPStatus.OK)
def post_compare_salary(
    payload: SalaryCreate = Body(),
    db: Session = Depends(get_db),
    # user: User = Depends(get_current_user),
):
    try:
        service = SalaryService()
        if (
            (len(payload.roles_compare_salary) != 2)
            or (len(payload.companies_compare_salary) != 2)
            or (len(payload.locations_compare_salary) != 2)
        ):
            raise CompareMoreThanTwoValuesFailedException()
        else:
            req_salary = SalaryCreate(
                roles_compare_salary=payload.roles_compare_salary,
                companies_compare_salary=payload.companies_compare_salary,
                locations_compare_salary=payload.locations_compare_salary,
            )

            payload_json = jsonable_encoder(req_salary)
            salary = service.compare_salary(db, payload=payload_json)

            return salary
    except UnauthorizedOperationException as err:
        response = GenericAPIResponseModel(
            status=http.HTTPStatus.UNAUTHORIZED,
            message="You are not logged in!",
            error="Unauthorized: Failed to perform this operation. Try logging in with the required permissions."
        )
        return build_api_response(response)
    except CompareMoreThanTwoValuesFailedException as err:
        response = GenericAPIResponseModel(
            status=http.HTTPStatus.BAD_REQUEST,
            message="You must input two roles, companies, and locations.",
            error=str(err)
        )
        return build_api_response(response)
    except Exception as err:
        logger.error(err.__str__())
        raise HTTPException(status_code=500, detail="Internal Server Error")
