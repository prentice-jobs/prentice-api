from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from pydantic import (
    UUID4,
    BaseModel,
    EmailStr,
    Field,
)

from src.core.schema import (
    PrenticeBaseSchema
)

class CheckUserRegisteredSchema(BaseModel):
    email: EmailStr

class RegisterSchema(BaseModel):
    firebase_uid: str
    email: EmailStr
    display_name: Optional[str]
    photo_url: Optional[str]
    email_verified: bool

class UserPreferencesSchema(BaseModel):
    # https://stackoverflow.com/questions/61326020/how-can-i-set-max-string-field-length-constraint-in-pydantic
    # Setting max length to avoid DB insertion errors
    role: str = Field(..., max_length=255) 
    industry: str = Field(..., max_length=255)
    location: str = Field(..., max_length=255)

class UserPreferencesResponseSchema(UserPreferencesSchema, PrenticeBaseSchema):
    user_id: UUID4

class RegisterResponseSchema(BaseModel):
    email: EmailStr
    created_at: datetime

class UserModelSchema(RegisterSchema, PrenticeBaseSchema):
    pass

# Firebase Schemas
class UserFirebaseFieldSchema(BaseModel):
    identities: dict
    sign_in_provider: str

class FirebaseUserSchema(BaseModel):
    name: str
    picture: str
    
    iss: str
    aud: str
    auth_time: int
    user_id: str
    
    sub: str
    iat: int
    exp: int
    
    email: EmailStr
    email_verified: bool
    firebase: UserFirebaseFieldSchema
    
    uid: str

class FirebaseUserResponseSchema(BaseModel):
    user: FirebaseUserSchema