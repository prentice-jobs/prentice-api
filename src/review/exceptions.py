class CreateCompanyReviewFailedException(Exception):
    def __init__(self, message="Error while creating a company review"):
        super().__init__(message)
        self.message = message


class CompanyReviewNotFoundException(Exception):
    def __init__(self, message="Company review does not exist"):
        super().__init__(message)
        self.message = message

class CreateReviewCommentFailedException(Exception):
    def __init__(self, message="Error while creating a review comment"):
        super().__init__(message)
        self.message = message 

class CreateCommentLikeFailedException(Exception):
    def __init__(self, message="Error while liking a comment"):
        super().__init__(message)
        self.message = message 

# RECSYS RELATED ERRORS
class RecsysVectorizerNotFoundException(Exception):
    def __init__(self, message="Cannot find RecSys Vectorizer object."):
        super().__init__(message)
        self.message = message 

class CreateSimScoresFailedException(Exception):
    def __init__(self, message="Failed to create UserReviewSimilarityScores object."):
        super().__init__(message)
        self.message = message