import uuid
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY

Base = declarative_base()

class Salaries(Base):
    __tablename__ = "salaries"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    roles_compare_salary = Column(
        ARRAY(
            Enum(
                "Software Engineer Intern",
                "Data Engineer",
                "Data Analyst",
                "Web Developer",
                "DevOps Engineer Intern",
                name="role_enum",
            )
        ),
        nullable=False,
    )
    companies_compare_salary = Column(
        ARRAY(Enum("Gojek", "Grab", "Tokopedia", "Traveloka", "maxim", name="company_enum")),
        nullable=False,
    )
    locations_compare_salary = Column(
        ARRAY(Enum("Jakarta", "Bandung", "Bogor", "Tangerang", "Balikpapan", name="location_enum")),
        nullable=False,
    )
