from datetime import datetime

from pydantic import (
    BaseModel,
    UUID4
)

class PrenticeBaseObject(BaseModel):
    """
    Abstract Pydantic schema for Prentice
    """

    id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: bool