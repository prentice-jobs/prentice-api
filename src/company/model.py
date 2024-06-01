from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class CompanyReview(Base):
    __tablename__ = "company_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_text = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    display_name = Column(String(225))
    description = Column(String(255))
    logo_url = Column(String)

    star_rating = Column(Float, nullable=False, default=0)
    tags = Column(ARRAY(String), nullable=True, unique=False)
    company_sentiment = Column(Integer, nullable=False, default=0)  # nanti diubah lg

    review_count = Column(Integer, nullable=False, default=0)
