import uuid
from http import HTTPStatus

from pydantic import (
    EmailStr
)

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from src.core.schema import GenericAPIResponseModel
from src.utils.time import get_datetime_now_jkt

from src.review.constants.temporary import FEED_REVIEWS_DUMMY

class ReviewService:
    # Business Logic methods
    @classmethod
    def fetch_feed(cls):
        # TODO
        return GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully fetched Review recommendations",
            data=FEED_REVIEWS_DUMMY,
        )

    # Utility methods