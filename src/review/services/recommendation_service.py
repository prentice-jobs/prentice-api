import pandas as pd
import random
import string
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

import uuid
from typing import (
    List,
    Dict,
    Any,
)
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

from src.review.model import (
    CompanyReview,
    ReviewComment,
    UserReviewSimilarityScores,
    UserReviewRecommendationsCache
)

from src.review.schema import (
    CreateUserReviewSimScoresSchema,
    UserReviewSimScoresModelSchema,
    CompanyReviewModelSchema,
)
from src.review.exceptions_recsys import (
    CreateSimScoresFailedException,
)
from src.review.constants import messages as ReviewMessages

from src.review.exceptions_recsys import (
    RecsysVectorizerNotFoundException,
    NoReviewsAvailableInPlatformException,
    NoUsersAvailableInPlatformException,
    BadRequestException,
)

from src.review.schema_recsys import (
    UniversalSimScoreSchema,

    ComputeSimNewUser_Review,
    ComputeSimNewUser_NewUserInput,

    ComputeSimNewReview_User,
    ComputeSimNewReview_NewReviewInput,
)

# TODO delete and adjust with ML model response
from src.review.constants.temporary import FEED_REVIEWS_DUMMY

from src.utils.time import get_datetime_now_jkt

class RecommendationService:
    # Business logic methods
    @classmethod
    def compute_similarity_for_new_user(
        cls,
        user: User,
        session: Session,
    ):
        """
        Driver method for ML algorithm `_compute_similarity_for_new_user()`
        """
        # Load vectorizer object
        vectorizer = CloudStorageService().fetch_recsys_vectorizer()

        if vectorizer is None:
            raise RecsysVectorizerNotFoundException()

        # Fetch UserPreferences of newly created user
        new_user_preferences = session.query(
                UserPreferences
            ) \
            .filter(
                UserPreferences.user_id == user.id,
                UserPreferences.is_deleted == False,
            ) \
            .one()
        
        # Create query to fetch Review data using SQLAlchemy
        review_query = session.query(
                CompanyReview.id, 
                CompanyReview.role, 
                CompanyReview.tags, 
                CompanyReview.location,
            )

        if review_query.count() == 0:
            logger.error("Error: NoReviewsAvailableInPlatformException")

            raise NoReviewsAvailableInPlatformException()

        # Fetch Reviews table and parse to df
        reviews_df = pd.read_sql(
                sql=review_query.statement,
                con=sqlalchemy_engine,
            ) \
            .rename(
                columns={
                    # Rename according to ML algo spec
                    'role': 'preferred_role',
                    'tags': 'preferred_industry',
                    'location': 'preferred_location'
                }
            )
        
        list_of_reviews: List[ComputeSimNewUser_Review] = \
            reviews_df.to_dict(orient='records')

        # Compute similarity for new user
        ml_algo_payload = ComputeSimNewUser_NewUserInput(
            id=user.id, # New user's id
            preferred_role=new_user_preferences.role,
            preferred_industry=new_user_preferences.industry,
            preferred_location=new_user_preferences.location,
            list_of_reviews=list_of_reviews,
            vectorizer=vectorizer,
        )

        new_user_sim_scores = cls.__compute_similarity_for_new_user(
            payload=ml_algo_payload,
        )

        created_count = cls.__save_sim_scores_to_db(
            new_sim_scores_list=new_user_sim_scores,
            session=session,
            user=user,
        )

        response = GenericAPIResponseModel(
            status=HTTPStatus.CREATED,
            message=f"Created {created_count} SimScore objects in db",
        )

        logger.info("Successfully recomputed SimScore Matrix for New User")

        return response

    @classmethod
    def compute_similarity_for_new_review(
        cls, 
        target_review_id: UUID4,
        session: Session,
    ):
        """
        Driver method for ML algorithm "_compute_similarity_for_new_review()"
        """
        # Load vectorizer object
        vectorizer = CloudStorageService().fetch_recsys_vectorizer()

        if vectorizer is None:
            raise RecsysVectorizerNotFoundException()

        # Create query to fetch Review data using SQLAlchemy
        users_query = session.query(
                UserPreferences.user_id,
                UserPreferences.role,
                UserPreferences.industry,
                UserPreferences.location,
            )

        if users_query.count() == 0:
            logger.error("Error: NoUsersAvailableInPlatformException")

            raise NoUsersAvailableInPlatformException()

        # Parse SQL to pandas df
        users_pref_df = pd.read_sql(
                sql=users_query.statement,
                con=sqlalchemy_engine,
            ) \
            .rename(
                columns={
                    # Rename according to ML algo spec
                    'role': 'preferred_role',
                    'industry': 'preferred_industry',
                    'location': 'preferred_location'
                }
            )
            
        list_of_users: List[ComputeSimNewReview_User] = \
            users_pref_df.to_dict(orient='records')

        # Compute similarity for new user
        review = session.query(CompanyReview) \
            .filter(
                CompanyReview.id == target_review_id, 
                CompanyReview.is_deleted == False
            ) \
            .first()
        
        if review is None:
            raise BadRequestException()
        
        ml_algo_payload = ComputeSimNewReview_NewReviewInput(
            id=review.id,
            review_role=review.role,
            review_industry=review.tags, # NOTE `tags` -> maps to `industry`
            review_location=review.location,
            list_of_users=list_of_users,
            vectorizer=vectorizer,
        )

        new_review_sim_scores = cls.__compute_similarity_for_new_review(
            payload=ml_algo_payload,
        )

        created_count = cls.__save_sim_scores_to_db(
            new_sim_scores_list=new_review_sim_scores,
            session=session,
            review=review,
        )

        response = GenericAPIResponseModel(
            status=HTTPStatus.CREATED,
            message=f"Created {created_count} SimScore objects in db",
        )

        logger.info("Successfully recomputed SimScore Matrix for New Review")

        return response
    
    @classmethod
    def recommend_reviews(
        cls,
        user: User,
        session: Session,
        top_n: int = 5,
        random_factor: float = 0.4,
        location_weight: float = 2.0,
    ):
        # Fetch UserPreferences of the User
        user_preferences = session.query(UserPreferences) \
                            .filter(
                                UserPreferences.user_id == user.id,
                                UserPreferences.is_deleted == False,
                            ) \
                            .first()
        
        
        if user_preferences is None:
            # TODO change to custom Exception
            raise Exception()

        prentice_all_reviews = session.query(CompanyReview) \
                                .filter(CompanyReview.is_deleted == False) \
                                .all()
        
        if len(prentice_all_reviews) == 0:
            # TODO change to custom Exception
            raise Exception()
        
        sim_scores_user = session.query(UserReviewSimilarityScores) \
                            .filter(
                                UserReviewSimilarityScores.user_id == user.id,
                                UserReviewSimilarityScores.is_deleted == False,
                            ) \
                            .all()
        
        if len(sim_scores_user) == 0:
            # TODO change to custom Exception
            raise Exception()
        
        review_recommendations = cls.__recommend_reviews(
            preferred_role=user_preferences.role,
            preferred_industry=user_preferences.industry,
            preferred_location=user_preferences.location,

            all_reviews=prentice_all_reviews,
            sim_scores_user=sim_scores_user,
            top_n=top_n,
        )

        if len(review_recommendations) == 0:
            logger.info(f"review_recommendations for {user.id}: {user.email} returned an empty list.")

        data_json = jsonable_encoder(review_recommendations)

        response = GenericAPIResponseModel(
            status=HTTPStatus.OK,
            message="Successfully generated review recommendations",
            data=data_json
        )

        return response

    @classmethod
    def __compute_similarity_for_new_user(
        cls, 
        payload: ComputeSimNewUser_NewUserInput,
    ):
        ''' Function #1 - to compute similarity score for new user to all of the existing reviews '''
        '''
        type Review = {'id': 193585,
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
            id: 1, # New User's UUID
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

        # Payload unpacking
        user_id = payload.id
        preferred_role = payload.preferred_role
        preferred_industry = payload.preferred_industry
        preferred_location = payload.preferred_location
        list_of_reviews = payload.list_of_reviews
        vectorizer = payload.vectorizer

        # Core ML Algorithm
        new_user_combined = ' '.join([preferred_role, preferred_industry, preferred_location])
        new_user_tfidf = vectorizer.transform([new_user_combined])

        # Hitung kemiripan antara pengguna baru dengan semua ulasan
        existing_reviews_combined = [f"{review.preferred_role} {review.preferred_industry} {review.preferred_location}" for review in list_of_reviews]
        new_user_sim_scores = cosine_similarity(new_user_tfidf, vectorizer.transform(existing_reviews_combined))
        
        sim_scores_with_ids: List[UniversalSimScoreSchema] = \
            [
                UniversalSimScoreSchema(
                    user_id=user_id, 
                    review_id=review.id, 
                    # NOTE - ROUND TO 3 DECIMAL DIGITS TO AVOID FLOATING POINT ERRORS
                    sim_score=round(score, 3), 
                ) \
                for review, score in zip(list_of_reviews, new_user_sim_scores[0])
            ]

        return sim_scores_with_ids
    
    @classmethod
    def __compute_similarity_for_new_review(
        cls, 
        payload: ComputeSimNewReview_NewReviewInput,
    ):
        ''' Function #2 - to compute similarity score for new review to all of the existing users '''
        '''
        type User = {
                    'id': 1,
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
            id: 1,
            review_role: 'Data Scientist Intern',
            review_industry: 'Healthcare',
            review_location: 'Jakarta',
            list_of_users: User[],
            vectorizer: TfidfVectorizer()
        }

        compute_similarity_for_new_review(input: NewReviewInput) = {
        output: SimScore[]
        }
        '''

        # Payload unpacking
        review_id = payload.id
        review_role = payload.review_role
        review_industry = payload.review_industry
        review_location = payload.review_location
        list_of_users = payload.list_of_users
        vectorizer =  payload.vectorizer

        # new_review_details adalah list yang berisi [role_str, tags_str, location_str]
        new_review_combined = ' '.join([review_role, review_industry, review_location])
        new_review_tfidf = vectorizer.transform([new_review_combined])

        # Hitung kemiripan antara semua pengguna dengan ulasan baru
        existing_users_combined = [f"{user_item.preferred_role} {user_item.preferred_industry} {user_item.preferred_location}" for user_item in list_of_users]
        new_review_sim_scores = cosine_similarity(vectorizer.transform(existing_users_combined), new_review_tfidf).reshape(1, -1)
        
        sim_scores_with_ids: List[UniversalSimScoreSchema] = \
            [
                UniversalSimScoreSchema(
                    user_id=user_item.user_id, # Uses user_id and NOT id!
                    review_id=review_id,
                    # NOTE - ROUND TO 3 DECIMAL DIGITS TO AVOID FLOATING POINT ERRORS
                    sim_score=round(score, 3), 
                ) \
                for user_item, score in zip(list_of_users, new_review_sim_scores[0])
            ]

        return sim_scores_with_ids
    

    @classmethod
    def __recommend_reviews(
        cls, 
        preferred_role,  
            # User's preferred role
        preferred_industry, 
            # User's preferred industry
            # NOTE - not given additional weight as the others,
        preferred_location, 
            # User's preferred location
        all_reviews: List[CompanyReview],
            # List[Review]
        sim_scores_user: List[UniversalSimScoreSchema], 
        top_n=5, 
        random_factor=0.4, 
        location_weight=2.0
    ):
        '''Function #3 - to get top_n recommended reviews'''

        '''
        type Review = {'id': 193585, # UUID
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
            sim_scores_user: SimScore[],  
                // List of SimScore only for specified user_id
                // Filter based on user_id
            top_n: 100,
            random_factor: 0.6,
            location_weight: 2.0
        }

        recommend_reviews(input: RecsysInput) = {
        output: Review[]
        }
        '''
        nearby_location_ids_dict = {
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

        roles_list = ["Software Engineer Intern", "Quality Assurance Intern",
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

        adjusted_scores = sim_scores_user.copy()
        review_dict = {review.id : review for review in all_reviews}

        for score in adjusted_scores:
            if review_dict[score.review_id].location == preferred_location:
                score.sim_score *= location_weight

        # Adjust for role similarity
        for score in adjusted_scores:
            review_role = review_dict[score.review_id].role
            score.sim_score *= role_similarity_matrix[
                roles_list.index(preferred_role), 
                roles_list.index(review_role)
            ]

        # Sort the adjusted scores based on sim_score
        sorted_scores = sorted(adjusted_scores, key=lambda x: x.sim_score, reverse=True)

        # Get top review indices based on sorted scores
        top_review_ids = [score.review_id for score in sorted_scores]

        # Determine number of top and random reviews to select
        num_random_reviews = int(top_n * random_factor)
        num_top_reviews = top_n - num_random_reviews

        # Select top reviews
        top_reviews = [review_dict[review_id] for review_id in top_review_ids[:num_top_reviews]]

        # Select random reviews from the remaining ones
        remaining_ids = top_review_ids[num_top_reviews:]
        remaining_reviews = [review_dict[review_id] for review_id in remaining_ids]

        # Filter random reviews based on nearby locations
        nearby_ids = []
        for review_id in remaining_ids:
            review_location = review_dict[review_id].location
            if review_location in nearby_location_ids_dict.get(preferred_location, []):
                nearby_ids.append(review_id)

        # Randomly select from nearby reviews
        if nearby_ids:
            nearby_random_reviews = [
                review_dict[review_id] \
                for review_id in np.random.choice(
                    nearby_ids, 
                    min(num_random_reviews, 
                    len(nearby_ids)), 
                    replace=False
                )
            ]
        else:
            nearby_random_reviews = []

        # Combine top reviews and nearby random reviews
        combined_reviews = top_reviews + nearby_random_reviews

        # If the combined reviews are less than top_n, add more from the remaining pool
        if len(combined_reviews) < top_n:
            additional_reviews_needed = top_n - len(combined_reviews)
            additional_reviews = [review_dict[review_id] for review_id in remaining_ids[:additional_reviews_needed]]
            combined_reviews.extend(additional_reviews)

        # Shuffle the combined recommendations
        np.random.shuffle(combined_reviews)

        # Return the top_n reviews
        return combined_reviews[:top_n]
    
    # Utility methods

    @classmethod
    def __save_sim_scores_to_db(
        cls,
        new_sim_scores_list: List[UniversalSimScoreSchema],
        session: Session,
        user: User = None,
        review: CompanyReview = None,
    ):
        # NOTE - Since our many to many table acts as a similarity matrix
        #  that gets updated continuously, we must check whether a many to many
        #  relation exists and "replace" (delete-then-insert) 
        #  them with the updated relations.
        
        # Save a list of many-to-many SimScore object to DB
        # user_id is the same, with different review_ids (1 for each review in app)

        # If both `user` and `review` params aren't given, raise exception
        if not user and not review:
            raise CreateSimScoresFailedException("Failed to create SimScore objects. Both `user` and `review` params are not given.")
        
        # If both exists, then it's also an error
        if user and review:
            raise CreateSimScoresFailedException("Failed to create SimScore objects. Overloaded arguments where only 1 of them should exist.")

        # Check if user already has SimScore pair in DB. 
        # If yes, purge all the objects. Else, continue
        
        if user:
            is_sim_score_exists_and_purged = cls.__check_sim_score_exists_and_purge(
                session=session,
                user=user,
            )
        elif review:
            is_sim_score_exists_and_purged = cls.__check_sim_score_exists_and_purge(
                session=session,
                review=review,
            )

        # Compute the new SimScore pair
        sim_scores_dict_list: List[CreateUserReviewSimScoresSchema] = []

        for score_dict in new_sim_scores_list:
            item = CreateUserReviewSimScoresSchema(
                user_id=score_dict.user_id,
                review_id=score_dict.review_id,
                sim_score=score_dict.sim_score
            )

            sim_scores_dict_list.append(item)

        db_user_review_sim_scores = cls.__create_bulk_user_review_sim_scores_db(
            sim_scores_dict_list=sim_scores_dict_list,
            session=session,
        )

        created_count = len(db_user_review_sim_scores)

        return created_count

    @classmethod
    def __create_user_review_sim_scores_db(
        cls,
        payload: CreateUserReviewSimScoresSchema,
        session: Session,
    ):
        sim_scores_schema = cls.__create_user_review_sim_scores_schema(
            payload=payload,
        )

        sim_scores_obj = UserReviewSimilarityScores(**sim_scores_schema.model_dump())

        try:
            session.add(sim_scores_obj)
            session.commit()
            session.refresh(sim_scores_obj)

            return sim_scores_obj
        except Exception as err:
            logger.error(err.__str__())
            
            session.rollback()
            raise CreateSimScoresFailedException(err.__str__())
        
    @classmethod
    def __create_bulk_user_review_sim_scores_db(
        cls,
        sim_scores_dict_list: List[CreateUserReviewSimScoresSchema],
        session: Session,
    ) -> List[UserReviewSimilarityScores]:
        # Use the more efficient, `session.add_all(List[obj])` API

        sim_scores_model_schemas: List[UserReviewSimilarityScores] = []
        for score in sim_scores_dict_list:
            model_schema: UserReviewSimScoresModelSchema = cls.__create_user_review_sim_scores_schema(
                payload=score,
            )

            model_db = UserReviewSimilarityScores(**model_schema.model_dump())

            sim_scores_model_schemas.append(model_db)

        try:
            session.add_all(sim_scores_model_schemas)
            session.commit()

            return sim_scores_model_schemas
        except Exception as err:
            logger.error(err.__str__())
            
            session.rollback()
            raise CreateSimScoresFailedException(err.__str__())

    @classmethod
    def __create_user_review_sim_scores_schema(
        cls,
        payload: CreateUserReviewSimScoresSchema,
    ) -> UserReviewSimScoresModelSchema:
        time_now = get_datetime_now_jkt()

        sim_scores_schema = UserReviewSimScoresModelSchema(
            id=uuid.uuid4(),
            created_at=time_now,
            updated_at=time_now,
            is_deleted=False,

            user_id=payload.user_id,
            review_id=payload.review_id,
            sim_score=payload.sim_score,
        )

        return sim_scores_schema
    
    @classmethod
    def __check_sim_score_exists_and_purge(
        cls,
        session: Session,
        user: User = None,
        review: CompanyReview = None,
    ):  
        # Check if user already has SimScore pair in DB. 
        # If yes, purge all the objects. Else, continue
        if (user and review) or (not user and not review):
            raise CreateSimScoresFailedException()
        
        existing_sim_scores = None

        if user:
            existing_sim_scores = session.query(UserReviewSimilarityScores) \
                .filter(
                    UserReviewSimilarityScores.user_id == user.id,
                    UserReviewSimilarityScores.is_deleted == False,
                )
        elif review:
            existing_sim_scores = session.query(UserReviewSimilarityScores) \
                .filter(
                    UserReviewSimilarityScores.review_id == review.id,
                    UserReviewSimilarityScores.is_deleted == False,
                )
            
        if existing_sim_scores.count() > 0:
            # Purge previous SimScores
            existing_sim_scores.delete()
            session.commit()

            return True
        else:
            return False