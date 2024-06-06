import uuid
from pydantic import (
    EmailStr
)
from sqlalchemy.orm import Session

from src.account.model import User
from src.account.schema import (
    RegisterSchema,
    UserModelSchema
)
from src.account.exceptions import (
    UserAlreadyExistsException,
    RegistrationFailedException,
)
from src.utils.time import get_datetime_now_jkt

class AccountService:   
    # Business logic methods
    @classmethod
    def check_user_is_registered(
        cls,
        session: Session,
        user_email: EmailStr,
    ) -> bool:
        """
        Checks whether the user is registered on Prentice or not
        """
        user = cls.get_user_by_email(session=session, email=user_email)
        
        if user:
            return True
        
        return False
    
    @classmethod
    def register_user(
        cls,
        session: Session,
        payload: RegisterSchema
    ) -> User:
        user = cls.get_user_by_email(session=session, email=payload.email)

        if user:
            raise UserAlreadyExistsException(
                user_email=user.email
            )
        
        try:
            return cls.create_prentice_user(session=session, payload=payload)
        except RegistrationFailedException as err:
            raise err

    # Utility methods
    @staticmethod
    def get_user_by_email(
        session: Session,
        email: EmailStr
    ) -> User | None:
        """
        Fetch a user from Prentice's User database based on email
        """
        user = session.query(User) \
                .filter(User.email == email, User.is_deleted == False) \
                .first()
        
        return user
    
    @staticmethod
    def get_user_by_firebase_uid(
        session: Session,
        firebase_uid: str,
    ) -> User | None:
        """
        Fetch a user from Prentice's User database based on their firebase_uid
        """

        user = session.query(User) \
                .filter(User.firebase_uid == firebase_uid, User.is_deleted == False) \
                .first()
        
        return user
    
    @staticmethod
    def _create_prentice_user_schema(
        payload: RegisterSchema,
    ) -> UserModelSchema:
        time_now_jkt = get_datetime_now_jkt()

        return UserModelSchema(
            id=uuid.uuid4(),
            created_at=time_now_jkt,
            updated_at=time_now_jkt,
            is_deleted=False,

            firebase_uid=payload.firebase_uid,
            email=payload.email,
            display_name=payload.display_name,
            photo_url=payload.photo_url,
            email_verified=payload.email_verified
        )
    
    @classmethod
    def create_prentice_user(
        cls,
        session: Session,
        payload: RegisterSchema,
    ) -> User:
        user_model_schema = cls._create_prentice_user_schema(payload=payload)

        user_obj_db = User(**user_model_schema.model_dump())

        try:
            session.add(user_obj_db)
            session.commit()
            session.refresh(user_obj_db)

            return user_obj_db
        except Exception as err:
            session.rollback()
            raise RegistrationFailedException(err.__str__())

