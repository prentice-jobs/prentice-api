import uuid
from src.utils.time import get_datetime_now_jkt
from src.review.schema import CompanyReviewModelSchema

company_ids = {
    "Gojek": "78ee6382-1a3d-4248-bf90-e6ef43fcb6ce",
    "Traveloka": "43b75c29-0ff2-417a-88a2-c651b91914a6",
}

review_1 = {
    "id": "510e0de3-0b56-4d1c-984c-1f217791046d",
    "company_id": company_ids["Gojek"],
    "author_id": "0689457c-f1bb-4e60-80b9-6fda8c1ca3c0",

    "location": "Jakarta",
    "is_remote": False,
    "star_rating": 4.5,

    "title": "Great compensation, wow!",
    "description": """I've been with the company for 5 years now. It taught me to work with systems at scale, which was very interesting. Also the compensation is top of market. I really enjoy the benefits here""",
    "role": "Software Engineer",
    
}


time_now = get_datetime_now_jkt()

FEED_REVIEWS_DUMMY = [
    CompanyReviewModelSchema(
        id=review_1["id"],
        created_at=time_now,
        updated_at=time_now,
        is_deleted=False,

        company_id=review_1["company_id"],
        author_id=review_1["author_id"],
        location=review_1["location"],
        is_remote=review_1["is_remote"],
        tags=["Fintech", "Backend"],
        star_rating=review_1["star_rating"],
        
        title=review_1["title"],
        description=review_1["description"],
        role=review_1["role"],
        start_date=time_now,
        end_date=time_now,
        offer_letter_url="www.gojek.com",
        annual_salary=45 * 10e6 * 12, # IDR 45 mn
        salary_currency="IDR",
    )
]