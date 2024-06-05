from typing import Optional
from pydantic import (
    UUID4,
    BaseModel,
    EmailStr
)

class CheckUserRegisteredSchema(BaseModel):
    email: EmailStr

