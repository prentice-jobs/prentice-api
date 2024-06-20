from http import HTTPStatus
from typing_extensions import Annotated
from sqlalchemy.orm import Session

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from fastapi.responses import (
    JSONResponse,
)

from fastapi.encoders import jsonable_encoder

from src.utils.db import get_db
from src.core.schema import GenericAPIResponseModel
from src.utils.response_builder import build_api_response
from src.account.model import User

from src.account.schema import  (
    CheckUserRegisteredSchema,
    RegisterSchema,
    UserPreferencesSchema,
)

from src.account.service import AccountService
from src.account.security import get_current_user
from src.account.exceptions import (
    UserAlreadyExistsException,
    RegistrationFailedException,
    SavePreferencesFailedException,
    UserPreferencesAlreadyExistsException,
)

VERSION = "v1"
ENDPOINT = "account"

account_router = APIRouter(
    prefix=f"/{VERSION}/{ENDPOINT}",
    tags=[ENDPOINT]
)

@account_router.post("/exists", status_code=HTTPStatus.OK, response_model=bool)
def check_user_registered(
    payload: CheckUserRegisteredSchema = Body(),
    session: Session = Depends(get_db),
):
    is_registered = AccountService.check_user_is_registered(
        session=session, 
        user_email=payload.email,
    )

    return is_registered

@account_router.post("/register", status_code=HTTPStatus.CREATED, response_model=GenericAPIResponseModel)
def register(
    payload: RegisterSchema = Body(),
    session: Session = Depends(get_db),
):
    try:
        response: GenericAPIResponseModel = AccountService.register_user(session=session, payload=payload)
        
        return build_api_response(response)
    except UserAlreadyExistsException as err:
        # TODO refactor to use client errors `HTTPException` for non-server logic type errors 
        # https://fastapi.tiangolo.com/reference/exceptions/
        response = GenericAPIResponseModel(
            status=HTTPStatus.CONFLICT,
            message=err.__str__(),
            error=err.__str__(),
        )

        return build_api_response(response)
    except RegistrationFailedException as err:
        response = GenericAPIResponseModel(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=err.__str__(),
            error=err.__str__(),
        )

        return build_api_response(response)

@account_router.post("/preferences", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def save_user_preferences(
    payload: UserPreferencesSchema = Body(),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        response: GenericAPIResponseModel = AccountService.save_user_preferences(
            payload=payload,
            session=session,
            user=user,
        )

        return build_api_response(response)
    except UserPreferencesAlreadyExistsException as err:
        response = GenericAPIResponseModel(
            status=HTTPStatus.CONFLICT,
            message=err.message,
            error=err.message,
        )

        return build_api_response(response)
    except SavePreferencesFailedException as err:
        response = GenericAPIResponseModel(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=err.message,
            error=err.message,
        )

        return build_api_response(response)

@account_router.get("/", status_code=HTTPStatus.OK)
def fetch_user_info(
    prentice_user: User = Depends(get_current_user),
):
    
    return prentice_user