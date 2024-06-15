from sqlalchemy.orm import Session

from src.review.model import (
    CompanyReview,
)

class ReviewService:

    def get_all_reviews(self, db: Session):
        get_all = db.query(CompanyReview).all()
        return [
            {
                key: value
                for key, value in vars(review).items()
                if not key.startswith("_")
            }
            for review in get_all
        ]
