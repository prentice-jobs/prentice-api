from datetime import datetime
from typing import (
    Optional,
    List,
)
from typing_extensions import (
    Annotated
)
from pydantic import (
    Field,
    UUID4,
    BaseModel,
)

from src.core.schema import (
    PrenticeBaseSchema
)

# Simple Models
class CreateCompanyReviewSchema(BaseModel):
    """Schema for user's input when creating new Company Review objects"""
    company_id: UUID4
    location: Annotated[str, Field(max_length=200)]
    is_remote: bool

    tags: List[Annotated[str, Field(max_length=495)]] # Decrease limit into 495 in case need to add `[` or `]`
    star_rating: Annotated[float, Field(strict=True, le=5, ge=0)] # Float from 0.0 - 5.0

    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str, Field(max_length=5000)]
    role: Annotated[str, Field(min_length=1, max_length=255)]

    start_date: datetime
    end_date: datetime

    offer_letter_url: str # URL to object storage for uploaded Offer Letter
    annual_salary: int # 64-bit Python-primitive integer type
    salary_currency: Annotated[str, Field(min_length=1, max_length=3)] # ISO 4217 3-letter currency code
    

class CompanyReviewModelSchema(CreateCompanyReviewSchema, PrenticeBaseSchema):
    """Schema for creating CompanyModel SQLAlchemy Objects"""
    author_id: UUID4

class CreateCompanyReviewResponseSchema(BaseModel):
    id: UUID4
    created_at: datetime

    author_id: UUID4
    company_id: UUID4
    
    title: Annotated[str, Field(min_length=1, max_length=255)]


class CreateCommentSchema(BaseModel):
    """Schema for user input in creating CompanyReview Comment objects """
    review_id: UUID4
    content: Annotated[str, Field(max_length=1000)]

class CommentModelSchema(CreateCommentSchema, PrenticeBaseSchema):
    """Schema for creating CompanyReviewComment SQLAlchemy objects"""
    author_id: UUID4
    likes_count: int

class CreateCommentLikeSchema(BaseModel):
    """Schema for user input in creating CompanyReview Comment Likes"""
    review_comment_id: UUID4

class CommentLikeModelSchema(CreateCommentLikeSchema, PrenticeBaseSchema):
    liker_id: UUID4
    
class CreateUserReviewSimScoresSchema(BaseModel):
    """
    Pydantic schema for creating `UserReviewSimilarityScores` and `UserReviewRecommendationsCache` objects
    """

    user_id: UUID4
    review_id: UUID4
    sim_score: Annotated[float, Field(ge=0, le=1)]

class UserReviewSimScoresModelSchema(CreateUserReviewSimScoresSchema, PrenticeBaseSchema):
    pass