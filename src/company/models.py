from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    TIMESTAMP,
    Float,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base

from src.utils.time import get_datetime_now_jkt

Base = declarative_base()


class Companies(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        default=get_datetime_now_jkt, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=get_datetime_now_jkt, nullable=False)
    is_deleted = Column(Boolean, nullable=True, default=False)
    display_name = Column(String(length=225), nullable=False)
    description = Column(String(length=255), nullable=True)
    logo_url = Column(String(length=225), nullable=False)
    star_rating = Column(Float(precision=1), nullable=False)
    company_sentiment = Column(Float(precision=1), nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    company_review = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
