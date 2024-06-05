from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime


class CompanyBase(BaseModel):
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None
    display_name: str
    logo_url: str
    star_rating: float
    company_sentiment: float
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    review_count: Optional[int] = None
    company_review: Optional[List[UUID4]] = None


class CompanyCreate(CompanyBase):
    id: UUID4


class CompanyUpdate(CompanyBase):
    id: UUID4


class Company(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    class Config:
        orm_mode = True


class CompanyJSONRequestSchema(BaseModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    display_name: str
    logo_url: str
    star_rating: float
    company_sentiment: float
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    review_count: Optional[int] = None
    company_review: Optional[List[UUID4]] = None


class CompanyUpdate(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: Optional[bool] = None

    class Config:
        orm_mode = True


class CompanyInDBBase(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True


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
