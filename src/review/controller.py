from http import HTTPStatus
from typing_extensions import Annotated

from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,
)

from fastapi.responses import (
    JSONResponse,
)

from fastapi.encoders import jsonable_encoder

from src.utils.db import get_db
from src.core.schema import GenericAPIResponseModel
from src.utils.response_builder import build_api_response

from src.review.service import ReviewService

# TODO delete and adjust with ML model response
from src.review.constants.temporary import (
    FEED_REVIEWS_DUMMY
)

VERSION = "v1"
ENDPOINT = "review"

review_router = APIRouter(
    prefix=f"/{VERSION}/{ENDPOINT}",
    tags=[ENDPOINT]
)

@review_router.get("/feed", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def fetch_user_feed(
    # TODO add arguments based on ML model spec
):
    response: GenericAPIResponseModel = ReviewService.fetch_feed()
    
    return build_api_response(response)

