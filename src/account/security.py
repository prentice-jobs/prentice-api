from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

import firebase_admin.auth as firebase_auth
from typing_extensions import Annotated

from prentice_logger import logger
from src.utils.db import get_db
from src.account.exceptions import (
    FirebaseTokenVerificationException,
    UnauthorizedOperationException,
)
from src.account.service import AccountService
from src.account.model import User
from src.account.schema import (
    FirebaseUserSchema,
    FirebaseUserResponseSchema,
    UserFirebaseFieldSchema,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

jwt_security = HTTPBearer(auto_error=True)

# Alternative Implementation
def verify_firebase_token(credentials: HTTPAuthorizationCredentials) -> dict | None:
    """
    Uses Firebase ID token from Bearer to identify firebase user id
    Args:
        token : the bearer token. Can be None as we set auto_error to False
    Returns:
        dict: the firebase user on success
    Raises:
        HTTPException 401 if user does not exist or token is invalid
    """
    try:
        token = str(credentials.credentials)

        if not token:
            raise UnauthorizedOperationException()
        
        user = firebase_auth.verify_id_token(token)
        
        return user
    except Exception as err:
        raise FirebaseTokenVerificationException(
            detail=f"Error verifying token: {err.__str__()}",
        ) # HTTPException
    
def convert_firebase_dict_to_pydantic(firebase_user_dict: dict) -> FirebaseUserResponseSchema:
    """
    Convert Firebase response `dict` to Pydantic object
    """
    try:
        firebase_user = FirebaseUserResponseSchema(
            user=FirebaseUserSchema(
                name=firebase_user_dict["name"],
                picture=firebase_user_dict["picture"],

                iss=firebase_user_dict["iss"],
                aud=firebase_user_dict["aud"],
                auth_time=firebase_user_dict["auth_time"],
                user_id=firebase_user_dict["user_id"],

                sub=firebase_user_dict["sub"],
                iat=firebase_user_dict["iat"],
                exp=firebase_user_dict["exp"],

                email=firebase_user_dict["email"],
                email_verified=firebase_user_dict["email_verified"],
                firebase=UserFirebaseFieldSchema(
                    identities=firebase_user_dict["firebase"]["identities"],
                    sign_in_provider=firebase_user_dict["firebase"]["sign_in_provider"],
                ),
                uid=firebase_user_dict["uid"],
            )
        )

        return firebase_user
    except KeyError as err:
        raise KeyError(f"Failed to serialize Firebase User dict: {err.__str__()}")
        
class JWTBearer(HTTPBearer):
    """
    Custom HTTPBearer class to represent JWT Bearer Tokens
    """
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        logger.debug(credentials)

        firebase_user_dict: (dict | None) = verify_firebase_token(credentials)
        
        if not firebase_user_dict:
            raise UnauthorizedOperationException()
        
        firebase_user: FirebaseUserResponseSchema = convert_firebase_dict_to_pydantic(
            firebase_user_dict=firebase_user_dict,
        )
        
        if credentials and firebase_user:
            return firebase_user # Firebase Token

def get_current_user(
    firebase_user: FirebaseUserResponseSchema = Depends(JWTBearer()),
    session: Session = Depends(get_db),
):
    """
    Core security middleware that performs user authorization and returns a custom Prentice User
    """
    prentice_user: User = AccountService.get_user_by_firebase_uid(
        session=session,
        firebase_uid=firebase_user.user.uid
    )

    return prentice_user