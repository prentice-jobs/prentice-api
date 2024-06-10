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
        
        user = firebase_auth.verify_id_token(token.credentials)
        
        return user
    except Exception as err:
        raise FirebaseTokenVerificationException(
            detail=f"Error verifying token: {err.__str__()}",
        ) # HTTPException

def get_current_user(
    session: Session = Depends(get_db),
    firebase_user: str = Depends(verify_firebase_token),
) -> User | None:
    logger.debug(firebase_user)

    firebase_uid = firebase_user["uid"]
    user = AccountService.get_user_by_firebase_uid(session=session, firebase_uid=firebase_uid)
    
    return user 
    
class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials and verify_firebase_token(credentials):
            return credentials.credentials