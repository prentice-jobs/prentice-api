from pydantic import BaseModel
from typing import List, Optional


class SentimentScoreBase(BaseModel):
    score: float


class SentimentScoreCreate(SentimentScoreBase):
    pass


class SentimentScore(SentimentScoreBase):
    id: int

    class Config:
        orm_mode = True


class CompanyReviewBase(BaseModel):
    review_text: str


class CompanyReviewCreate(CompanyReviewBase):
    pass


class CompanyReview(CompanyReviewBase):
    id: int

    class Config:
        orm_mode = True


class CompanyBase(BaseModel):
    display_name: str
    description: str
    logo_url: str
    star_rating: float
    tags: List[str]
    review_count: int


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyInDBBase(CompanyBase):
    id: int
    company_sentiment: Optional[SentimentScore] = None
    reviews: List[CompanyReview] = []

    class Config:
        orm_mode = True


class Company(CompanyInDBBase):
    pass
