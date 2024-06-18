from http import HTTPStatus
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from src.account.model import User
from src.salary.services.get_all_reviews_service import ReviewService
from src.salary.models import Salaries
from src.company.service import CompanyService
from src.core.schema import GenericAPIResponseModel
import logging

logger = logging.getLogger(__name__)

class SalaryService:

    @classmethod
    def compare_salary(cls, db: Session, payload: dict):
        try:
            salary = Salaries(**payload)
            result = []

            service = ReviewService()
            company_service = CompanyService()

            def generate_result_object(review, company):
                company_id = review.get('company_id')
                logo_url = None
                company_reviews = None

                if company_id:
                    try:
                        company_data = company_service.find_company_by_id(db=db, company_id=company_id)
                        logo_url = company_data.data.get("logo_url")
                        company_reviews = company_data.data.get("company_reviews")

                    except Exception as e:
                        logger.error(f"Error fetching company data for company_id {company_id}: {e}")

                return {
                    "role": review.get("role"),
                    "company": company,
                    "date_posted": review.get("start_date"), 
                    "logo_url": logo_url,
                    "annual_salary": jsonable_encoder(
                        review.get("annual_salary")
                    ),
                    "company_rating": jsonable_encoder(
                        review.get("star_rating")
                    ),
                    "company_reviews": company_reviews
                }

            for i, review in enumerate(service.get_all_reviews(db=db)):
                if (str(review.get("role")) == str(salary.roles_compare_salary[0]) and
                    str(review.get("location")) == str(salary.locations_compare_salary[0])):
                    result.append(generate_result_object(review, salary.companies_compare_salary[0]))
                    break

            for i, review in enumerate(service.get_all_reviews(db=db)):
                if (str(review.get("role")) == str(salary.roles_compare_salary[1]) and
                    str(review.get("location")) == str(salary.locations_compare_salary[1])):
                    result.append(generate_result_object(review, salary.companies_compare_salary[1]))
                    break

            response = GenericAPIResponseModel(
                status=HTTPStatus.OK,
                message="Successfully compared companies' salaries",
                data=result,
            )
                
            return response
        except UnauthorizedOperationException as err:
            logger.error(f"Unauthorized operation: {err}")
            raise err
        except Exception as err:
            logger.error(f"Unknown exception occurred: {err}", exc_info=True)
            raise err
