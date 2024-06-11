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
    SmallInteger,
    Integer,
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
    company_id = Column(UUID())
    author_id = Column(UUID())
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
    annual_salary = Column(BigInteger())
    salary_currency = Column(String(3)) # ISO 4217
    

class ReviewSentiment(PrenticeBaseModel):
    __tablename__ = "review_sentiments"
    
    review_id = Column(UUID())
    sentiment_score = Column(SmallInteger()) # SentimentScore{ -1, 0, +1 }
    sentiment = Column(String(30))

class ReviewComment(PrenticeBaseModel):
    __tablename__ = "review_comments"

    review_id = Column(UUID())
    author_id = Column(UUID())
    likes_count = Column(Integer())

class ReviewCommentLike(PrenticeBaseModel):
    __tablename__ = "review_comment_likes"

    review_comment_id = Column(UUID())
    liker_id = Column(UUID())

