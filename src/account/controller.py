from http import HTTPStatus

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

from enum import Enum

from src.utils.db import get_db
from src.account.schema import  (
    CheckUserRegisteredSchema,
    RegisterSchema,
    RegisterResponseSchema
)

from src.account.service import AccountService
from src.account.exceptions import (
    UserAlreadyExistsException,
    RegistrationFailedException
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
    session = Depends(get_db),
):
    return AccountService.check_user_is_registered(
        session=session, 
        user_email=payload.email,
    )

@account_router.post("/register", status_code=HTTPStatus.CREATED, response_model=RegisterResponseSchema)
def register(
    payload: RegisterSchema = Body(),
    session = Depends(get_db)
):
    try:
        new_user = AccountService.register_user(session=session, payload=payload)
        
        response = RegisterResponseSchema(
            email=new_user.email, 
            created_at=new_user.created_at
        )
        
        response_json = jsonable_encoder(response)

        return JSONResponse(
            status_code=HTTPStatus.CREATED,
            content=response_json
        )
    except UserAlreadyExistsException as err:
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=err.__str__()
        )
    except RegistrationFailedException as err:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=err.__str__()
        )
    
