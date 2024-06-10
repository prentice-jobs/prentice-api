class CreateCompanyReviewFailedException(Exception):
    def __init__(self, message="Error while creating a new company review"):
        super().__init__(message)
        self.message = message