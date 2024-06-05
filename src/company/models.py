from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    String,
    Integer,
    Enum,
    CheckConstraint,
    TIMESTAMP,
    text,
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

from src.utils.time import get_datetime_now_jkt

import uuid

Base = declarative_base()


class CompanyReview(Base):  # for development necessity
    __tablename__ = "company_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_text = Column(String)


class Companies(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4(), unique=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        default=get_datetime_now_jkt, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),
                        default=get_datetime_now_jkt, nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    display_name = Column(String(225))
    description = Column(String(255))
    logo_url = Column(String)

    star_rating = Column(Float, nullable=False, default=0)
    tags = Column(ARRAY(String), nullable=True, unique=False)
    company_sentiment = Column(
        Integer, nullable=False, default=0)  # for development necessity

    review_count = Column(Integer, nullable=False, default=0)
