import uuid

from sqlalchemy import (
    Column,
    UUID,
    TIMESTAMP,
    Boolean
)

from src.utils.db import Base
from src.utils.time import get_datetime_now_jkt

class PrenticeBaseObjectModel(Base):
    """
    Abstract data model for Prentice
    """
    
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4(), unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=get_datetime_now_jkt, onupdate=get_datetime_now_jkt, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    