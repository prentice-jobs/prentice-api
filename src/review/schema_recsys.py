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


# 1 - Compute Similarity for New User
class ComputeSimNewUser_Review(BaseModel):
    id: UUID4
    preferred_role: str
    preferred_industry: str 
        # NOTE - Assume Review.tags is the industry tags for review
    preferred_location: str

class ComputeSimNewUser_SimScore(BaseModel):
    user_id: UUID4
    review_id: UUID4
    sim_score: float

class ComputeSimNewUser_NewUserInput(BaseModel):
    id: UUID4 # 
    preferred_role: str
    preferred_industry: str
    preferred_location: str
    list_of_reviews: List[ComputeSimNewUser_Review]
    vectorizer: Any

# 2 - Compute Similarity for New Review

# 3 - Recommend Reviews