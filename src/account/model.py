import uuid
from uuid import UUID
from pytz import timezone
from datetime import datetime

from src.utils.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    UUID,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    TIMESTAMP
)
from sqlalchemy.orm import (
    Session,
    relationship
)

from src.core.model import PrenticeBaseModel

class User(PrenticeBaseModel):
    __tablename__ = "users"

    # NOTE - firebase_uid is unique only across a single app - flush database before migrating to production firebase app
    firebase_uid = Column(String(255))
    email = Column(String(255), unique=True)
    display_name = Column(String(255), nullable=True)
    photo_url = Column(String, nullable=True)
    email_verified = Column(Boolean)

    # Table relations
    preferences = relationship(
        "UserPreferences", 
        uselist=False,  # Converts many-to-one -> one-to-one
        back_populates="user"
    )
    
class UserPreferences(PrenticeBaseModel):
    __tablename__ = "user_preferences"
    
    role = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship(
        "User", 
        uselist=False,
        back_populates="preferences"
    )
    
