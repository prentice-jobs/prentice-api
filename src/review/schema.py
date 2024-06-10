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

class CreateCompanyReviewSchema(BaseModel):
    """Schema for user's input when creating new Company Review"""
    company_id: UUID4
    location: Annotated[str, Field(max_length=200)]
    is_remote: bool

    tags: List[Annotated[str, Field(max_length=500)]]
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
    