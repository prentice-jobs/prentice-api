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

USER_MODEL_NAME = "User"

class User(PrenticeBaseModel):
    __tablename__ = "users"

    # NOTE - firebase_uid is unique only across a single app - flush database before migrating to production firebase app
    firebase_uid = Column(String(255), unique=True)
    email = Column(String(255), unique=True)
    display_name = Column(String(255), nullable=True)
    photo_url = Column(String, nullable=True)
    email_verified = Column(Boolean)
    
class UserPreferences(PrenticeBaseModel):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship(USER_MODEL_NAME, back_populates="preferences")
    is_active = Column(Boolean)
    
    role = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)