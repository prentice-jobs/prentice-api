import uuid
from http import HTTPStatus
from sqlalchemy.orm import Session

from pydantic import UUID4

from fastapi import (
    APIRouter,
    Depends,
    Body,

    File,
    UploadFile,
)


from src.core.schema import GenericAPIResponseModel

from src.account.model import User
from src.account.security import get_current_user

from src.utils.db import get_db
from src.utils.response_builder import build_api_response

from src.review.services.review_service import ReviewService
from src.review.services.gcs_service import CloudStorageService
from src.review.services.comment_service import CommentService
from src.review.services.likes_service import LikesService
from src.review.services.recommendation_service import RecommendationService

from src.review.schema import (
    CreateCompanyReviewSchema,
    CreateCommentSchema,
    CreateCommentLikeSchema,
    ComputeSimNewReviewRequest,
)

from src.review.utils import CommentLikeActions

from prentice_logger import logger


VERSION = "v1"
ENDPOINT = "review"

review_router = APIRouter(
    prefix=f"/{VERSION}/{ENDPOINT}",
    tags=[ENDPOINT]
)

@review_router.post("/recsys/new-user", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def compute_sim_new_user(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        response = RecommendationService.compute_similarity_for_new_user(
            user=user,
            session=session,
        )

        return build_api_response(response)
    except Exception as err:
        response = GenericAPIResponseModel(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=err.__str__(),
            error=err.__str__()
        )

        return build_api_response(response)

@review_router.post("/recsys/new-review", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def compute_sim_new_review(
    payload: ComputeSimNewReviewRequest = Body(),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user), # Authorization purposes
):
    try:
        review_id = uuid.UUID(payload.review_id)
        response: GenericAPIResponseModel = RecommendationService.compute_similarity_for_new_review(
            target_review_id=review_id,
            session=session,
        )
        
        return build_api_response(response)
    except Exception as err:
        response = GenericAPIResponseModel(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=err.__str__(),
            error=err.__str__()
        )

        return build_api_response(response)

@review_router.post("/recsys", status_code=HTTPStatus.OK, response_model=GenericAPIResponseModel)
def recommend_reviews(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        # Hyperparameter for recommendation list length
        TOP_N = 5

        response: GenericAPIResponseModel =  RecommendationService.recommend_reviews(
            user=user,
            session=session,
            top_n=TOP_N,
        )

        return build_api_response(response)
    except Exception as err:
        response = GenericAPIResponseModel(
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=err.__str__(),
            error=err.__str__()
        )

        return build_api_response(response) 


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
    response: GenericAPIResponseModel = CommentService.create_comment(
        payload=payload,
        session=session,
        user=user,
    )

    return build_api_response(response)

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
    response: GenericAPIResponseModel = CloudStorageService().upload_file(
        file=file, 
        user_id=user.id,
    )

    return build_api_response(response)