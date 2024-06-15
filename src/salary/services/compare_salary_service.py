from http import HTTPStatus
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from src.account.model import User
from src.salary.services.get_all_reviews_service import ReviewService
from src.salary.models import Salaries
from src.company.service import CompanyService
from src.core.schema import GenericAPIResponseModel

class SalaryService:

    @classmethod
    def compare_salary(cls, db: Session, payload: dict):
        try:
            salary = Salaries(**payload)
            company_service = CompanyService()
            result = []
            company_reviews = []     

            service = ReviewService()

            def generate_result_object(review, company, company_reviews):
                return {
                    "role": review.get("role"),
                    "company": company,
                    "date_posted": review.get("start_date"), 
                    "logo_url": company_service.get_company_by_id(db=db, company_id=review.get('company_id'))["logo_url"],
                    "annual_salary": jsonable_encoder(
                        review.get("annual_salary")
                    ),
                    "company_rating": jsonable_encoder(
                        review.get("star_rating")
                    ),
                    "company_reviews": company_service.get_company_by_id(db=db, company_id=review.get('company_id'))["company_reviews"]
                }

            for i, review in enumerate(service.get_all_reviews(db=db)):

                if str(review.get("role")) == str(salary.roles_compare_salary[0]) and str(
                    review.get("location")
                ) == str(salary.locations_compare_salary[0]):
                    company_reviews.append({"title": review.get("title"),
                    "description": review.get("description")})
                    result.append(generate_result_object(review, salary.companies_compare_salary[0], company_reviews))
                    company_reviews = []
                    break
                
            for i, review in enumerate(service.get_all_reviews(db=db)):

                if str(review.get("role")) == str(salary.roles_compare_salary[1]) and str(
                    review.get("location")
                ) == str(salary.locations_compare_salary[1]):
                    company_reviews.append({"title": review.get("title"),
                    "description": review.get("description")})
                    result.append(generate_result_object(review, salary.companies_compare_salary[1], company_reviews))
                    company_reviews = []
                    break

            response = GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully compare companies's salary",
                data=result,
            )
                
            return response
        except UnauthorizedOperationException as err:
            raise err
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err.__str__()}")

            raise err