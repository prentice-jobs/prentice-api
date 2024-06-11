from datetime import datetime
from typing import Optional
from pydantic import (
    UUID4,
    BaseModel,
    EmailStr
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