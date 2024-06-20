import uuid
from http import HTTPStatus

from pydantic import (
    EmailStr
)

from prentice_logger import logger
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from src.core.schema import GenericAPIResponseModel
from src.utils.time import get_datetime_now_jkt

from src.account.model import (
    User,
    UserPreferences,
)

from src.account.schema import (
    RegisterSchema,
    UserModelSchema,
    RegisterResponseSchema,
    UserPreferencesSchema,
    UserPreferencesResponseSchema,
)
from src.account.exceptions import (
    UserAlreadyExistsException,
    RegistrationFailedException,
    SavePreferencesFailedException,
    UserPreferencesAlreadyExistsException,
)

from src.account.constants import messages as AccountMessages

from src.review.services.recommendation_service import RecommendationService

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
    ) -> GenericAPIResponseModel:
        user = cls.get_user_by_email(session=session, email=payload.email)

        if user:
            raise UserAlreadyExistsException(user_email=user.email)
        
        try:
            user = cls._create_prentice_user(session=session, payload=payload)

            data = RegisterResponseSchema(
                email=user.email, 
                created_at=user.created_at
            )

            # RECSYS - Compute Similarity Score Matrix
            RecommendationService.compute_similarity_for_new_user(
                user=user,
                session=session,
            )

            data_json = jsonable_encoder(data)

            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=AccountMessages.CREATE_NEW_USER_SUCCESS,
                data=data_json,
            )

            return response
        except RegistrationFailedException as err:
            raise err
        except Exception as err:
            raise err
        

    @classmethod
    def save_user_preferences(
        cls,
        payload: UserPreferencesSchema,
        session: Session,
        user: User,
    ):
        # Check if user has a UserPreferences already or not
        existing_user_preference = session.query(UserPreferences) \
            .filter(
                UserPreferences.user_id == user.id, 
                UserPreferences.is_deleted == False
            ) \
            .one_or_none()
        
        if existing_user_preference is not None:
            raise UserPreferencesAlreadyExistsException()

        # If None, go ahead and create user_prefs
        time_now = get_datetime_now_jkt()
        user_preferences_schema = UserPreferencesResponseSchema(
            id=uuid.uuid4(),
            created_at=time_now,
            updated_at=time_now,
            is_deleted=False,

            role=payload.role,
            industry=payload.industry,
            location=payload.location,

            is_active=True,
            user_id=user.id,
        )

        user_preference_db = UserPreferences(**user_preferences_schema.model_dump())

        try:
            session.add(user_preference_db)
            session.commit()

            data_json = jsonable_encoder(user_preference_db)
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=AccountMessages.SAVE_USER_PREFERENCES_SUCCESS,
                data=data_json,
            )

            return response
        except Exception as err:
            logger.error(f"Error while saving user preferences: {err.__str__()}")

            raise SavePreferencesFailedException(err.__str__())

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
    def _create_prentice_user(
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

