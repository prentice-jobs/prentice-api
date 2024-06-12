import uuid
from http import HTTPStatus

from fastapi import (
    Depends
)

from pydantic import (
    EmailStr,
    UUID4
)

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from prentice_logger import logger

from src.account.model import User
from src.account.exceptions import UnauthorizedOperationException

from src.core.schema import GenericAPIResponseModel

from src.review.schema import (
    CreateCommentSchema,
    CommentModelSchema,
    CreateCommentLikeSchema,
    CommentLikeModelSchema,
)

from src.review.model import ReviewComment, ReviewCommentLike
from src.review.exceptions import (
    CreateCommentLikeFailedException,
)
from src.review.constants import messages as ReviewMessages

from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.utils.time import get_datetime_now_jkt

class LikesService:
    # Business logic methods
    @classmethod
    def create_comment_like(
        cls,
        payload: CreateCommentLikeSchema,
        session: Session,
        user: User,
    ):
        try:
            comment_like = cls._create_comment_like_model(
                payload=payload,
                session=session,
                user=user,
            )

            data_json = jsonable_encoder(comment_like)
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.LIKE_COMMENT_CREATE_SUCCESS,
                data=data_json,
            )

            return response
        except CreateCommentLikeFailedException as err:
            raise err
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")
            
            raise err
    
    # Utility methods
    @classmethod
    def _create_comment_like_model(
        cls,
        payload: CreateCommentLikeSchema,
        session: Session,
        user: User,
    ):
        comment_like_schema = cls._create_comment_like_schema(
            payload=payload,
            user=user,
        )

        comment_like_obj = ReviewCommentLike(**comment_like_schema.model_dump())

        try:
            session.add(comment_like_obj)
            session.commit()
            session.refresh(comment_like_obj)

            return comment_like_obj
        except Exception as err:
            session.rollback()
            raise CreateCommentLikeFailedException(err.__str__())

    @classmethod
    def _create_comment_like_schema(
        cls,
        payload: CreateCommentLikeSchema,
        user: User,
    ):
        time_now = get_datetime_now_jkt()

        comment_like_model_schema = CommentLikeModelSchema(
            id=uuid.uuid4(),
            created_at=time_now,
            updated_at=time_now,
            is_deleted=False,
            
            review_comment_id=payload.review_comment_id,
            liker_id=user.id,
        )

        return comment_like_model_schema