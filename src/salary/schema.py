from pydantic import BaseModel, UUID4
from enum import Enum
from typing import List


class RoleCompareSalaryEnum(str, Enum):
    software_engineer = "Software Engineer"
    data_engineer = "Data Engineer"
    data_analyst = "Data Analyst"


class CompanyCompareSalaryEnum(str, Enum):
    gojek = "Gojek"
    grab = "Grab"
    tokopedia = "Tokopedia"
    traveloka = "Traveloka"


class LocationSalaryEnum(str, Enum):
    jakarta = "Jakarta"
    bandung = "Bandung"
    bogor = "Bogor"
    tangerang = "Tangerang"


class SalaryBase(BaseModel):
    roles_compare_salary: List[RoleCompareSalaryEnum]
    companies_compare_salary: List[CompanyCompareSalaryEnum]
    locations_compare_salary: List[LocationSalaryEnum]


class SalaryCreate(SalaryBase):
    id: UUID4


class Salary(SalaryBase):
    id: UUID4

    class Config:
        orm_mode = True
