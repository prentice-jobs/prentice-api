class CompareCompaniesSalariesFailedException(Exception):
    def __init__(self, message="Error while comparing companies' salaries"):
        super().__init__(message)
        self.message = message


class CompareMoreThanTwoValuesFailedException(Exception):
    def __init__(self, message="Cannot compare more than two roles/companies/locations"):
        super().__init__(message)
        self.message = message
