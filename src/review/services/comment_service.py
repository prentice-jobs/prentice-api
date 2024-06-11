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
from src.utils.time import get_datetime_now_jkt

from src.review.schema import (
    CreateCommentSchema,
    CommentModelSchema,
)

from src.review.model import ReviewComment
from src.review.exceptions import (
    CreateReviewCommentFailedException,
)
from src.review.constants import messages as ReviewMessages

from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.utils.time import get_datetime_now_jkt

class CommentService:
    # Business Logic methods
    @classmethod
    def create_comment(
        cls,
        payload: CreateCommentSchema,
        session: Session,
        user: User,
    ): 
        try:
            review_comment = cls._create_review_comment_model(
                payload=payload,
                session=session,
                user=user,
            )

            data_json = jsonable_encoder(review_comment)
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.REVIEW_COMMENT_CREATE_SUCCESS,
                data=data_json,
            )
            
            return response
        except CreateReviewCommentFailedException as err:
            raise err
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")
            
            raise err

    # Utility methods
    @classmethod
    def _create_review_comment_model(
        cls,
        payload: CreateCommentSchema,
        session: Session,
        user: User,
    ):
        review_comment_schema = cls._create_review_comment_schema(
            payload=payload,
            user=user,
        )

        review_comment_obj = ReviewComment(**review_comment_schema.model_dump())

        try:
            session.add(review_comment_obj)
            session.commit()
            session.refresh(review_comment_obj)

            return review_comment_obj
        except Exception as err:
            session.rollback()
            raise CreateReviewCommentFailedException(err.__str__())

    @classmethod
    def _create_review_comment_schema(
        cls,
        payload: CreateCommentSchema,
        user: User,
    ):
        time_now = get_datetime_now_jkt()

        review_comment_model_schema = CommentModelSchema(
            id=uuid.uuid4(),
            created_at=time_now,
            updated_at=time_now,
            is_deleted=False,

            review_id=payload.review_id,
            content=payload.content,

            author_id=user.id,
            likes_count=0, # Initial likes_count = 0
        )

        return review_comment_model_schema
