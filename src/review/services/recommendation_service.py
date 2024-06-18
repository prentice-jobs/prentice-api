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

from src.utils.db import engine as sqlalchemy_engine
from src.account.model import (
    User, 
    UserPreferences,
)
from src.account.exceptions import UnauthorizedOperationException
from src.account.constants import messages as AccountMessages

from src.review.services.gcs_service import CloudStorageService

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

from src.review.exceptions import RecsysVectorizerNotFoundException

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
        user: User,
        session: Session,
    ):
        # Load vectorizer object
        vectorizer = CloudStorageService().fetch_recsys_vectorizer()

        if vectorizer is None:
            raise RecsysVectorizerNotFoundException()

        # Create query to fetch 4 columns of Review table using SQLAlchemy
        query = session.query(
                CompanyReview.id, 
                CompanyReview.role, 
                CompanyReview.tags, 
                CompanyReview.location,
            ) 

        # Parse SQL to pandas df
        reviews_df = pd.read_sql(
            sql=query.statement,
            con=sqlalchemy_engine,
        )
            
        list_of_reviews = reviews_df.to_dict(orient='records')

        # Compute similarity for new user
        # TODO review_id field is now `id` only
        new_user_sim_scores = cls._compute_similarity_for_new_user(
            user_id=user.id,
            preferred_role=preferred_role,
            preferred_industry=preferred_industry,
            preferred_location=preferred_location,
            list_of_reviews=list_of_reviews,
            vectorizer=vectorizer,
        )

        return new_user_sim_scores

    @classmethod
    def compute_similarity_for_new_review(
        cls, 
        preferred_role: str,
        preferred_industry: str,
        preferred_location: str,
        user: User,
        review: CompanyReview,
        session: Session,
    ):
        # Load vectorizer object
        vectorizer = CloudStorageService().fetch_recsys_vectorizer()

        if vectorizer is None:
            raise RecsysVectorizerNotFoundException()

        # Create query to fetch 4 columns of Users table using SQLAlchemy
        query = session.query(
                UserPreferences.user_id,
                UserPreferences.role,
                UserPreferences.industry,
                UserPreferences.location,
            ) 

        # Parse SQL to pandas df
        users_pref_df = pd.read_sql(
            sql=query.statement,
            con=sqlalchemy_engine,
        )
            
        list_of_users = users_pref_df.to_dict(orient='records')

        # Compute similarity for new user
        # TODO user_id field is now `id` only - change var names
        new_review_sim_scores = cls._compute_similarity_for_new_review(
            review_id=review.id,
            preferred_role=preferred_role,
            preferred_industry=preferred_industry,
            preferred_location=preferred_location,
            list_of_users=list_of_users,
            vectorizer=vectorizer,
        )

        return new_review_sim_scores
    
    @classmethod
    def recommend_reviews(preferred_role, preferred_industry, preferred_location, reviews, sim_scores_user, top_n=5, random_factor=0.4, location_weight=2.0):
        '''Function to get top_n recommended reviews'''

        '''
        type Review = {'review_id': 193585,
                        'company_id': 37,
                        'author_id': 830,
                        'location': 'Depok',
                        'is_remote': True,
                        'tags': 'Government',
                        'star_rating': 2,
                        'title': 'company yang bagus',
                        'description': 'pengalaman saya di sini sangat menyenangkan karena kerjanya jelas',
                        'role': 'Quality Assurance Intern'
                        }

        type SimScore = {
        'user_id': 2,
        'review_id': 4,
        'sim_score': 0.2
        }

        type RecsysInput = {
        preferred_role: 'Data Scientist Intern',
        preferred_industry: 'Healthcare',
        preferred_location: 'Jakarta',
        reviews: Review[],
        sim_scores_user: SimScore[],  // list of SimScore only for specified user_id
        top_n: 100,
        random_factor: 0.6,
        location_weight: 2.0
        }

        recommend_reviews(input: RecsysInput) = {
        output: Review[]
        }
        '''
        nearby_location_ids = {
            "Banda Aceh": ["Medan"],
            "Medan": ["Banda Aceh"],
            "Pekanbaru": ["Jambi"],
            "Jambi": ["Pekanbaru"],
            "Jakarta": ["Depok", "Bogor", "Bandung"],
            "Depok": ["Jakarta", "Bogor", "Bandung"],
            "Bogor": ["Jakarta", "Depok", "Bandung"],
            "Bandung": ["Jakarta", "Depok", "Bogor"],
            "Surabaya": ["Semarang", "Yogyakarta"],
            "Semarang": ["Surabaya", "Yogyakarta"],
            "Yogyakarta": ["Surabaya", "Semarang"],
            "Palangka Raya": ["Samarinda"],
            "Samarinda": ["Palangka Raya"]
        }

        roles = ["Software Engineer Intern", "Quality Assurance Intern",
                'Business Development Intern', "Data Scientist Intern",
                "Product Manager Intern", "UI/UX Designer Intern",
                'Business Analyst Intern', 'Data Analyst Intern']

        role_similarity_matrix = np.array([
            [1.0, 0.8, 0.2, 0.7, 0.6, 0.4, 0.5, 0.7], # SE Intern
            [0.8, 1.0, 0.2, 0.6, 0.5, 0.4, 0.5, 0.6], # QA Intern
            [0.2, 0.2, 1.0, 0.2, 0.5, 0.6, 0.8, 0.5], # BD Intern
            [0.7, 0.6, 0.2, 1.0, 0.6, 0.4, 0.5, 0.8], # DS Intern
            [0.6, 0.5, 0.5, 0.6, 1.0, 0.6, 0.7, 0.6], # PM Intern
            [0.4, 0.4, 0.6, 0.4, 0.6, 1.0, 0.6, 0.5], # UI/UX Intern
            [0.5, 0.5, 0.8, 0.5, 0.7, 0.6, 1.0, 0.7], # BA Intern
            [0.7, 0.6, 0.5, 0.8, 0.6, 0.5, 0.7, 1.0], # DA Intern
        ])

        # Adjust for location weight
        adjusted_scores = sim_scores_user.copy()
        review_locations = [review['location'] for review in reviews]

        for score in adjusted_scores:
            if review_locations[score['review_id'] - 1] == preferred_location:
                score['sim_score'] *= location_weight

        # Adjust for role similarity
        review_roles = [review['role'] for review in reviews]

        for score in adjusted_scores:
            review_role = review_roles[score['review_id'] - 1]
            score['sim_score'] *= role_similarity_matrix[roles.index(preferred_role), roles.index(review_role)]

        # Sort the adjusted scores based on sim_score
        sorted_scores = sorted(adjusted_scores, key=lambda x: x['sim_score'], reverse=True)

        # Get top review indices based on sorted scores
        top_review_indices = [score['review_id'] - 1 for score in sorted_scores]

        # Determine number of top and random reviews to select
        num_random_reviews = int(top_n * random_factor)
        num_top_reviews = top_n - num_random_reviews

        # Select top reviews
        top_reviews = [reviews[idx] for idx in top_review_indices[:num_top_reviews]]

        # Select random reviews from the remaining ones
        remaining_indices = top_review_indices[num_top_reviews:]
        remaining_reviews = [reviews[idx] for idx in remaining_indices]

        # Filter random reviews based on nearby locations
        nearby_indices = []
        for idx in remaining_indices:
            review_location = review_locations[idx]
            if review_location in nearby_location_ids.get(preferred_location, []):
                nearby_indices.append(idx)

        # Randomly select from nearby reviews
        if nearby_indices:
            nearby_random_reviews = [reviews[idx] for idx in np.random.choice(nearby_indices, min(num_random_reviews, len(nearby_indices)), replace=False)]
        else:
            nearby_random_reviews = []

        # Combine and ensure diversity in roles
        combined_reviews = pd.DataFrame(top_reviews + nearby_random_reviews).drop_duplicates(subset=['role']).head(top_n).to_dict(orient='records')

        # If the combined reviews are less than top_n, add more from the remaining pool
        if len(combined_reviews) < top_n:
            additional_reviews_needed = top_n - len(combined_reviews)
            additional_reviews = [reviews[idx] for idx in remaining_indices[:additional_reviews_needed]]
            combined_reviews.extend(additional_reviews)

        # Shuffle the combined recommendations
        np.random.shuffle(combined_reviews)

        return combined_reviews[:top_n]

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