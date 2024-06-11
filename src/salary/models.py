import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Enum, Column, String
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


class Salaries(Base):
    __tablename__ = "salaries"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    roles_compare_salary = Column(
        ARRAY(
            Enum("Software Engineer", "Data Engineer", "Data Analyst", name="role_enum")
        ),
        nullable=False,
    )
    companies_compare_salary = Column(
        ARRAY(Enum("Gojek", "Grab", "Tokopedia", "Traveloka", name="company_enum")),
        nullable=False,
    )
    locations_compare_salary = Column(
        ARRAY(Enum("Jakarta", "Bandung", "Bogor", "Tangerang", name="location_enum")),
        nullable=False,
    )
