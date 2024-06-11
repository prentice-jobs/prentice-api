from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from src.salary.models import Salaries
from src.review.constants.temporary import FEED_REVIEWS_DUMMY


class SalaryService:

    def compare_salary(self, payload: dict):
        salary = Salaries(**payload)
        result = []

        def generate_result_object(index, role_label):
            return {
                "role": role_label,
                "company_id": jsonable_encoder(FEED_REVIEWS_DUMMY[index].company_id),
                "company": "nama company",
                "currency": jsonable_encoder(FEED_REVIEWS_DUMMY[index].annual_salary),
                "company_rating": jsonable_encoder(FEED_REVIEWS_DUMMY[index].star_rating)
            }

        for i, review in enumerate(FEED_REVIEWS_DUMMY):
            if (str(review.role) == str(salary.roles_compare_salary[0])
                    and str(review.location) == str(salary.locations_compare_salary[0])):
                result.append(generate_result_object(i, "Role 1"))
                break

        for i, review in enumerate(FEED_REVIEWS_DUMMY):
            if (str(review.role) == str(salary.roles_compare_salary[1])
                    and str(review.location) == str(salary.locations_compare_salary[1])):
                result.append(generate_result_object(i, "Role 2"))
                break

        return result
