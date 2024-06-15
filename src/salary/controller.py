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
