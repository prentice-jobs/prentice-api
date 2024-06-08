from http import HTTPStatus
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Request,
    Response,
    Depends,
    Body,

    File,
    UploadFile,
)

from fastapi.responses import (
    JSONResponse,
)

from fastapi.encoders import jsonable_encoder
from src.core.schema import GenericAPIResponseModel

from src.account.model import User
from src.account.security import get_current_user

from src.utils.db import get_db
from src.utils.response_builder import build_api_response

from src.review.services.review_service import ReviewService
from src.review.schema import (
    CompanyReviewModelSchema,
    CreateCompanyReviewSchema,
)

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

@review_router.post("/", status_code=HTTPStatus.CREATED, response_model=GenericAPIResponseModel)
def create_new_review(
    payload: CreateCompanyReviewSchema = Body(),
    session: Session = Depends(get_db),
):
    pass

@review_router.post("/upload/offer-letter", status_code=HTTPStatus.OK, response_class=GenericAPIResponseModel)
def upload_offer_letter(
    user: User = Depends(get_current_user),
    offer_letter_file: UploadFile = File(...)
):
    pass