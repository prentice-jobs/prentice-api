import uuid
from uuid import UUID
from pytz import timezone
from datetime import datetime

from src.utils.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    Float,
    BigInteger,
    String,
    TIMESTAMP
)
from sqlalchemy.orm import (
    Session,
    relationship
)

from src.core.model import PrenticeBaseModel

class CompanyReview(PrenticeBaseModel):
    __tablename__ = "company_reviews"
    company_id = Column(UUID(as_uuid=True))
    author_id = Column(UUID(as_uuid=True))
    location = Column(String(200))
    is_remote = Column(Boolean())
    
    tags = Column(String(500))
    star_rating = Column(Float(precision=1))
    
    title = Column(String(255))
    description = Column(String())
    role = Column(String(255))
    
    start_date = Column(TIMESTAMP(timezone=True))
    end_date = Column(TIMESTAMP(timezone=True))
    
    offer_letter_url = Column(String())
    salary = Column(BigInteger())
    salary_currency = Column(String(3)) # ISO 4217
    

class ReviewSentiment(PrenticeBaseModel):
    __tablename__ = "review_sentiments"

class ReviewComment(PrenticeBaseModel):
    __tablename__ = "review_comments"

class ReviewCommentLike(PrenticeBaseModel):
    __tablename__ = "review_comment_likes"