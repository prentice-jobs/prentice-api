from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body
)

from enum import Enum

from src.utils.db import get_db
from src.account.schema import  (
    CheckUserRegisteredSchema
)

from src.account.service import AccountService

VERSION = "v1"
ENDPOINT = "account"

account_router = APIRouter(
    prefix=f"/{VERSION}/{ENDPOINT}",
    tags=[ENDPOINT]
)

@account_router.post("/exists")
def check_user_registered(
    payload: CheckUserRegisteredSchema = Body(),
    session = Depends(get_db)
):
    service = AccountService()
    
    return service.check_user_is_registered(
        session=session, user_email=payload.email
    )
