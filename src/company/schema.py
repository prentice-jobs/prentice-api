from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime


class CompanyBase(BaseModel):
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
    created_at: datetime
    updated_at: datetime

class CompanyCreateRequest(CompanyBase):
    pass


class CompanyName(BaseModel):
    display_name: str


class CompanyUpdate(CompanyBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime


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
