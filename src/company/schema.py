from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime


class CompanyBase(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    star_rating: Optional[float] = 0
    tags: Optional[List[str]] = []
    company_sentiment: Optional[int] = 0
    review_count: Optional[int] = 0


class CompanyCreate(CompanyBase):
    display_name: str
    description: str


class CompanyUpdate(CompanyBase):
    pass


class CompanyInDBBase(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True


class Company(CompanyInDBBase):
    pass


class CompanyReviewBase(BaseModel):
    review_text: Optional[str] = None


class CompanyReviewCreate(CompanyReviewBase):
    review_text: str


class CompanyReviewUpdate(CompanyReviewBase):
    pass


class CompanyReviewInDBBase(CompanyReviewBase):
    id: int

    class Config:
        orm_mode = True


class CompanyReview(CompanyReviewInDBBase):
    pass
