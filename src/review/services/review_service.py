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
    # Simple
    CreateCompanyReviewSchema,
    CompanyReviewModelSchema,
    CreateCompanyReviewResponseSchema,
)
from src.review.model import (
    CompanyReview,
    ReviewComment,
)

from src.review.exceptions import (
    CreateCompanyReviewFailedException,
    CompanyReviewNotFoundException,
)
from src.review.constants import messages as ReviewMessages

# TODO delete and adjust with ML model response
from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.utils.time import get_datetime_now_jkt

class ReviewService:
    # Business Logic methods
    @classmethod
    def fetch_feed(cls):
        # TODO integrate with ML model response
        return GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully fetched Review recommendations",
            data=FEED_REVIEWS_DUMMY,
        )
    
    @classmethod
    def fetch_review(
        cls, 
        review_id: UUID4,
        session: Session,
        user: User,
    ):
        try:
            review = session.query(CompanyReview) \
                    .filter(CompanyReview.id == review_id, CompanyReview.is_deleted == False) \
                    .order_by(CompanyReview.created_at) \
                    .first()
            
            if review is None:
                raise CompanyReviewNotFoundException()
            
            review_comments = session.query(ReviewComment) \
                                .filter(
                                    ReviewComment.review_id == review.id, 
                                    ReviewComment.is_deleted == False
                                    ) \
                                .order_by(ReviewComment.created_at) \
                                .all()
                                
            data = {
                "review": review,
                "comments": review_comments,
            }

            data_json = jsonable_encoder(data)
            
            return GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully fetched Company Review",
                data=data_json,
            )
        except Exception as err:
            raise Exception(f"Error while fetching review: {err.__str__()}")
        
    @classmethod
    def create_company_review(
        cls, 
        payload: CreateCompanyReviewSchema,
        session: Session,
        user: User,
    ):
        try:
            company_review = cls._create_company_review_model(
                payload=payload,
                session=session,
                user=user,
            )

            data = CreateCompanyReviewResponseSchema(
                id=company_review.id,
                created_at=company_review.created_at,
                author_id=company_review.author_id,
                company_id=company_review.company_id,
                title=company_review.title,
            )

            data_json = jsonable_encoder(data)

            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.COMPANY_REVIEW_CREATE_SUCCESS,
                data=data_json,
            )

            return response
        except UnauthorizedOperationException as err:
            raise err
        except CreateCompanyReviewFailedException as err:
            raise err
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")
            
            raise err

    # Utility methods
    @classmethod
    def _create_company_review_model(
        cls,
        payload: CreateCompanyReviewSchema,
        session: Session,
        user: User,
    ):
        company_review_schema = cls._create_company_review_schema(
            payload=payload, 
            user=user,
        )
            
        company_review_obj = CompanyReview(**company_review_schema.model_dump())

        try:
            session.add(company_review_obj)
            session.commit()
            session.refresh(company_review_obj)

            return company_review_obj
        except Exception as err: # To handle db exceptions
            session.rollback()
            raise CreateCompanyReviewFailedException(err.__str__())

    @classmethod
    def _create_company_review_schema(
        cls,
        payload: CreateCompanyReviewSchema,
        user: User,
    ):
        time_now = get_datetime_now_jkt()

        company_review_model_schema = CompanyReviewModelSchema(
            id=uuid.uuid4(),
            created_at=time_now,
            updated_at=time_now,
            is_deleted=False,

            company_id=payload.company_id,
            location=payload.location,
            is_remote=payload.is_remote,
            tags=payload.tags,
            star_rating=payload.star_rating,
            
            title=payload.title,
            description=payload.description,
            role=payload.role,
            start_date=payload.start_date,
            end_date=payload.end_date,

            offer_letter_url=payload.offer_letter_url,
            annual_salary=payload.annual_salary,
            salary_currency=payload.salary_currency,
            
            author_id=user.id,
        )

        return company_review_model_schema