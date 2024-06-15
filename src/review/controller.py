import uuid
from http import HTTPStatus
from typing_extensions import Annotated
from pydantic import (
    UUID4,
)
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
from src.account.exceptions import UnauthorizedOperationException
from src.account.security import get_current_user

from src.utils.db import get_db
from src.utils.response_builder import build_api_response

from src.review.services.review_service import ReviewService
from src.review.services.upload_service import UploadService
from src.review.services.comment_service import CommentService
from src.review.services.likes_service import LikesService

from src.review.schema import (
    CreateCompanyReviewSchema,
    CreateCommentSchema,
    CreateCommentLikeSchema,
)
from src.review.exceptions import (
    CreateCompanyReviewFailedException, 
    CompanyReviewNotFoundException,
    CreateReviewCommentFailedException,
)

from src.review.utils import CommentLikeActions

from prentice_logger import logger


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
    user: User = Depends(get_current_user),
):
    response: GenericAPIResponseModel = ReviewService.create_company_review(
        payload=payload,
        session=session,
        user=user,
    )

    return build_api_response(response)

@review_router.get("/{review_id}", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def fetch_review(
    review_id: str,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    review_uuid = uuid.UUID(review_id)
    response: GenericAPIResponseModel = ReviewService.fetch_review(
        review_id=review_uuid, 
        session=session,
        user=user,
    )
    
    return build_api_response(response)

@review_router.post("/comment", status_code=HTTPStatus.CREATED, response_model=GenericAPIResponseModel)
def create_comment(
    payload: CreateCommentSchema = Body(),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
): 
    try:
        response: GenericAPIResponseModel = CommentService.create_comment(
            payload=payload,
            session=session,
            user=user,
        )

        return build_api_response(response)
    except CreateReviewCommentFailedException as err:
        response = GenericAPIResponseModel(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=err.__str__(),
            error=err.__str__(),
        )

        return build_api_response(response)
    except Exception as err:
        logger.error(err.__str__())
        raise err

@review_router.post("/comment/like", status_code=HTTPStatus.CREATED, response_model=GenericAPIResponseModel)
def like_comment(
    payload: CreateCommentLikeSchema = Body(),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Create new Like objact in DB
    response: GenericAPIResponseModel = LikesService.create_comment_like(
        payload=payload,
        session=session,
        user=user,
    )

    # Increment Review Comment's likes_count value
    CommentService.update_comment_like(
        review_comment_id=payload.review_comment_id,
        session=session,
        action=CommentLikeActions.INCREMENT,
    )

    return build_api_response(response)


@review_router.post("/comment/unlike", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def unlike_comment(
    payload: CreateCommentLikeSchema = Body(),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    response: GenericAPIResponseModel = LikesService.delete_comment_like(
        payload=payload,
        session=session,
        user=user,
    )

    return build_api_response(response)

@review_router.post("/offer", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def upload_offer_letter(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    try:
        response: GenericAPIResponseModel = UploadService().upload_file(
            file=file, 
            user_id=user.id,
        )

        return build_api_response(response)
    except Exception as err:
        logger.error(err.__str__())
        raise err