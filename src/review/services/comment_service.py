import uuid
from enum import Enum
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
)

from src.review.model import ReviewComment
from src.review.exceptions import (
    CreateReviewCommentFailedException,
)
from src.review.constants import messages as ReviewMessages

from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.review.utils import CommentLikeActions

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
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.REVIEW_COMMENT_CREATE_FAILED,
                error=ReviewMessages.REVIEW_COMMENT_CREATE_FAILED,
            )

            return response
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.REVIEW_COMMENT_CREATE_FAILED,
                error=ReviewMessages.REVIEW_COMMENT_CREATE_FAILED,
            )

            return response
        
    @classmethod
    def update_comment_like(
        cls,
        review_comment_id: UUID4,
        session: Session,
        action = CommentLikeActions,
    ) -> None:
        """Increments or decrements a comment's like"""
        try:
            if action == CommentLikeActions.INCREMENT:
                ACTION_VALUE = 1
            else:
                ACTION_VALUE = -1

            review_comment = session.query(ReviewComment) \
                            .filter(
                                ReviewComment.id == review_comment_id,
                                ReviewComment.is_deleted == False
                                ) \
                            .one()
            
            
            new_likes_count = review_comment.likes_count + ACTION_VALUE
            review_comment.likes_count = new_likes_count

            session.commit()
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
