from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

import firebase_admin.auth as firebase_auth

from src.utils.db import get_db
from src.account.exceptions import FirebaseTokenVerificationException
from src.account.service import AccountService
from src.account.model import User

jwt_security = HTTPBearer(auto_error=True)

def firebase_verify_id_token(token: str = Depends(jwt_security)) -> str:
    try:
        decoded_token = firebase_auth.verify_id_token(id_token=token)
        firebase_uid = decoded_token["uid"]
        
        return firebase_uid
    except Exception as err:
        raise FirebaseTokenVerificationException(err.__str__())
    
def get_current_user(
    session: Session = Depends(get_db),
    firebase_uid: str = Depends(firebase_verify_id_token),
) -> User | None:
    user = AccountService.get_user_by_firebase_uid(session=session, firebase_uid=firebase_uid)
    
    return user

