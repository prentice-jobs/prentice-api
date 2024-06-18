import pandas as pd
import random
import string
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

import uuid
from http import HTTPStatus

from fastapi import (
    Depends
)

from pydantic import (
    EmailStr,
    UUID4
)

from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session

from prentice_logger import logger

from src.account.model import User
from src.account.exceptions import UnauthorizedOperationException
from src.account.constants import messages as AccountMessages

from src.core.schema import GenericAPIResponseModel
from src.utils.time import get_datetime_now_jkt

from src.review.schema import (
    # Simple
    CreateCompanyReviewSchema,
    CompanyReviewModelSchema,
    CreateCompanyReviewResponseSchema,
)
from src.review.model import (
    CompanyReview,
    ReviewComment,
)

from src.review.exceptions import (
    CreateCompanyReviewFailedException,
    CompanyReviewNotFoundException,
)
from src.review.constants import messages as ReviewMessages

# TODO delete and adjust with ML model response
from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.utils.time import get_datetime_now_jkt

class RecommendationService:
    # Business logic methods
    @classmethod
    def compute_similarity_for_new_user(
        cls, 
        preferred_role: str,
        preferred_industry: str,
        preferred_location: str,
    ):
        # Load vectorizer object

        # Fetch review from db and parse to pandas df

        # Fetch specific columns and convert pandas df to dict
        
        # Compute similarity for new user

        pass

    @classmethod
    def compute_similarity_for_new_review(
        cls, 
        preferred_role: str,
        preferred_industry: str,
        preferred_location: str,
    ):
        # Load vectorizer object

        # Fetch review from db and parse to pandas df

        # Fetch specific columns and convert pandas df to dict
        
        # Compute similarity for new review

        pass

    @classmethod
    def _compute_similarity_for_new_user(cls, user_id, preferred_role, preferred_industry, preferred_location, list_of_reviews, vectorizer):
        ''' Function to compute similarity score for new user to all of the existing reviews '''
        '''
        type Review = {'review_id': 193585,
                        'company_id': 37,
                        'author_id': 830,
                        'location': 'Depok',
                        'is_remote': True,
                        'tags': 'Government',
                        'star_rating': 2,
                        'title': 'P7KBT1FGUN',
                        'description': '7U2\t\x0cNLW2P1VE\x0c5DHN\x0c\x0bFGLZP8C6\x0b\r\x0bZBG1ZK3L\x0b5B Z\x0bQOL0V',
                        'role': 'Quality Assurance Intern'
                        }

        type SimScore = {
        'user_id': 2,
        'review_id': 4,
        'sim_score': 0.2
        }

        type NewUserInput = {
        user_id: 1,
        preferred_role: 'Data Scientist Intern',
        preferred_industry: 'Healthcare',
        preferred_location: 'Jakarta',
        list_of_reviews: Review[],
        vectorizer: TfidfVectorizer()
        }

        compute_similarity_for_new_user(input: NewUserInput) = {
        output: SimScore[]
        }
        '''

        new_user_combined = ' '.join([preferred_role, preferred_industry, preferred_location])
        new_user_tfidf = vectorizer.transform([new_user_combined])

        # Hitung kemiripan antara pengguna baru dengan semua ulasan
        existing_reviews_combined = [f"{d['role']} {d['tags']} {d['location']}" for d in list_of_reviews]
        new_user_sim_scores = cosine_similarity(new_user_tfidf, vectorizer.transform(existing_reviews_combined))
        sim_scores_with_ids = [{"user_id": user_id, "review_id": review['review_id'], "sim_score": score}
                            for review, score in zip(list_of_reviews, new_user_sim_scores[0])]

        return sim_scores_with_ids 
    
    def _compute_similarity_for_new_review(review_id, preferred_role, preferred_industry, preferred_location, list_of_users, vectorizer):
        ''' Function to compute similarity score for new review to all of the existing users '''
        '''
        type User = {'user_id': 1,
                    'preferred_role': 'Data Scientist Intern',
                    'preferred_industry': 'Healthcare',
                    'preferred_location': 'Jakarta'
                        }

        type SimScore = {
        'user_id': 2,
        'review_id': 4,
        'sim_score': 0.2
        }

        type NewReviewInput = {
        review_id: 1,
        preferred_role: 'Data Scientist Intern',
        preferred_industry: 'Healthcare',
        preferred_location: 'Jakarta',
        list_of_users: User[],
        vectorizer: TfidfVectorizer()
        }

        compute_similarity_for_new_review(input: NewReviewInput) = {
        output: SimScore[]
        }
        '''

        # new_review_details adalah list yang berisi [role_str, tags_str, location_str]
        new_review_combined = ' '.join([preferred_role, preferred_industry, preferred_location])
        new_review_tfidf = vectorizer.transform([new_review_combined])

        # Hitung kemiripan antara semua pengguna dengan ulasan baru
        existing_users_combined = [f"{d['preferred_role']} {d['preferred_industry']} {d['preferred_location']}" for d in list_of_users]
        new_review_sim_scores = cosine_similarity(vectorizer.transform(existing_users_combined), new_review_tfidf).reshape(1, -1)
        sim_scores_with_ids = [{"user_id": user['user_id'], "review_id": review_id, "sim_score": score}
                            for user, score in zip(list_of_users, new_review_sim_scores[0])]

        return sim_scores_with_ids

    # Utility methods