from pydantic import BaseModel, UUID4
from enum import Enum
from typing import List

class RoleCompareSalaryEnum(str, Enum):
    software_engineer = "Software Engineer Intern"
    data_engineer = "Data Engineer"
    data_analyst = "Data Analyst"
    web_developer = "Web Developer"


class CompanyCompareSalaryEnum(str, Enum):
    gojek = "Gojek"
    grab = "Grab"
    tokopedia = "Tokopedia"
    traveloka = "Traveloka"
    maxim = "maxim"


class LocationSalaryEnum(str, Enum):
    jakarta = "Jakarta"
    bandung = "Bandung"
    bogor = "Bogor"
    tangerang = "Tangerang"
    balikpapan = "Balikpapan"


class SalaryBase(BaseModel):
    roles_compare_salary: List[RoleCompareSalaryEnum]
    companies_compare_salary: List[CompanyCompareSalaryEnum]
    locations_compare_salary: List[LocationSalaryEnum]


class SalaryCreate(SalaryBase):
    pass


class Salary(SalaryBase):
    id: UUID4

    class Config:
        orm_mode = True
