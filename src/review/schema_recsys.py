from datetime import datetime
from typing import (
    Optional,
    List,
    Any,
)
from typing_extensions import (
    Annotated,
)
from pydantic import (
    Field,
    UUID4,
    BaseModel,
)


class UniversalSimScoreSchema(BaseModel):
    user_id: UUID4
    review_id: UUID4
    sim_score: float

# 1 - Compute Similarity for New User
class ComputeSimNewUser_Review(BaseModel):
    id: UUID4
    preferred_role: str
    preferred_industry: str 
        # NOTE - Assume Review.tags is the industry tags for review
    preferred_location: str


class ComputeSimNewUser_NewUserInput(BaseModel):
    id: UUID4 # User's ID
    preferred_role: str
    preferred_industry: str
    preferred_location: str
    list_of_reviews: List[ComputeSimNewUser_Review]
    vectorizer: Any

# 2 - Compute Similarity for New Review
class ComputeSimNewReview_User(BaseModel):
    user_id: UUID4
    preferred_role: str
    preferred_industry: str
    preferred_location: str

class ComputeSimNewReview_NewReviewInput(BaseModel):
    id: UUID4 # Review ID
    review_role: str
    review_industry: str
    review_location: str
    list_of_users: List[ComputeSimNewReview_User]
    vectorizer: Any

# 3 - Recommend Reviews