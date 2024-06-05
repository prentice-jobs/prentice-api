from sqlalchemy.orm import Session
from pydantic import (
    EmailStr
)

from src.account.model import User

class AccountService:
    def get_user_by_email(
        self,
        session: Session,
        user_email: EmailStr
    ) -> User | None:
        """
        Fetch a user from Prentice's User database based on email
        """

        user = session.query(User) \
                .filter(User.email == user_email, User.is_deleted == False) \
                .order_by(User.updated_at.desc()) \
                .first()
        
        return user
    
    def check_user_is_registered(
        self,
        session: Session,
        user_email: EmailStr,
    ) -> bool:
        """
        Checks whether the user is registered on Prentice or not
        """
        user = self.get_user_by_email(session=session,user_email=user_email)
        
        if user:
            return True
        
        return False