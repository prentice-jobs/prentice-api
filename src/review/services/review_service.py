import uuid
import os
from http import HTTPStatus

from pydantic import (
    EmailStr,
    UUID4
)

from fastapi.encoders import jsonable_encoder
import requests


from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)
from fastapi import HTTPException
from prentice_logger import logger

from src.account.model import (
    User, 
    UserPreferences,
)
from src.account.exceptions import UnauthorizedOperationException
from src.account.constants import messages as AccountMessages

from src.core.schema import GenericAPIResponseModel
from src.review.services.recommendation_service import RecommendationService

from src.review.schema import (
    # Simple
    CreateCompanyReviewSchema,
    CompanyReviewModelSchema,
    CreateCompanyReviewResponseSchema,
    SentimentAnalysisSchema
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

    API_URL = os.getenv("API_URL")
    headers = {"Authorization": f"Bearer {os.getenv('BEARER_TOKEN')}"}

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
        except CompanyReviewNotFoundException as err:
            response = GenericAPIResponseModel(
                status=HTTPStatus.NOT_FOUND,
                message=ReviewMessages.COMPANY_REVIEW_NOT_FOUND,
                error=ReviewMessages.COMPANY_REVIEW_NOT_FOUND,
            )

            return response
        except Exception as err:
            logger.error(f"Error while fetching review: {err.__str__()}")
        
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.FOR_YOU_FEED_ERROR,
                error=ReviewMessages.FOR_YOU_FEED_ERROR,
            )

            return response
        
    @classmethod
    def create_company_review(
        cls, 
        payload: CreateCompanyReviewSchema,
        session: Session,
        user: User,
    ):
        try:
            company_review_model = cls._create_company_review_model(
                payload=payload,
                session=session,
                user=user,
            )

            review_data = CreateCompanyReviewResponseSchema(
                id=company_review_model.id,
                created_at=company_review_model.created_at,
                author_id=company_review_model.author_id,
                company_id=company_review_model.company_id,
                title=company_review_model.title,
            )

            # RECSYS - Compute Similarity Score Matrix
            RecommendationService.compute_similarity_for_new_review(
                target_review_id=company_review_model.id,
                session=session,
            )
            
            review_data_json = jsonable_encoder(review_data)

            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.COMPANY_REVIEW_CREATE_SUCCESS,
                data=review_data_json,
            )

            return response
        except UnauthorizedOperationException as err:
            response = GenericAPIResponseModel(
                status=HTTPStatus.UNAUTHORIZED,
                message=AccountMessages.UNAUTHORIZED_ACTION_RECOMMENDATION,
                error=AccountMessages.UNAUTHORIZED_ACTION,
            )

            return response
        except CreateCompanyReviewFailedException as err:
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.COMPANY_REVIEW_CREATE_FAILED,
                error=err.__str__(),
            )
            
            return response
        except NoResultFound as err:
            response = GenericAPIResponseModel(
                status_code=HTTPStatus.NOT_FOUND,
                content=err.__str__(),
                error=err.__str__(),
            )

            return response
        except MultipleResultsFound as err:
            response = GenericAPIResponseModel(
                status_code=HTTPStatus.CONFLICT,
                content=err.__str__(),
                error=err.__str__(),
            )

            return response
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.GENERAL_ERROR,
                error=err.__str__(),
            )
            
            return response

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
        except Exception as err:
            logger.error(err.__str__())

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

    @classmethod
    def _query(cls, payload):
        response = requests.post(cls.API_URL, headers=cls.headers, json=payload)
        return response.json()

    @classmethod
    def query_sentiment_analysis(cls, text: SentimentAnalysisSchema):
        output = cls._query({"inputs": text})
        highest_score = -1
        highest_label = ""

        for sublist in output:
            for item in sublist:
                if item['score'] > highest_score:
                    highest_score = item['score']
                    highest_label = item['label']

        if 'error' in output:
            raise HTTPException(status_code=500, detail="Error with sentiment analysis API")
        
        response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.COMPANY_REVIEW_CREATE_SUCCESS,
                data={"label":highest_label},
        )
        
        return response