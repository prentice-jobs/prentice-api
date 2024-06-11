class CreateCompanyReviewFailedException(Exception):
    def __init__(self, message="Error while creating a new company review"):
        super().__init__(message)
        self.message = message


class CompanyReviewNotFoundException(Exception):
    def __init__(self, message="Company review does not exist"):
        super().__init__(message)
        self.message = message