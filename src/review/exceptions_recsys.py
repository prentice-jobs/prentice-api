# RECSYS RELATED ERRORS
class RecsysVectorizerNotFoundException(Exception):
    def __init__(self, message="Cannot find RecSys Vectorizer object."):
        super().__init__(message)
        self.message = message 

class CreateSimScoresFailedException(Exception):
    def __init__(self, message="Failed to create UserReviewSimilarityScores object."):
        super().__init__(message)
        self.message = message

class NoReviewsAvailableInPlatformException(Exception):
    def __init__(self, message="A minimum of 1 CompanyReview must exist on Prentice. It seems like we don't have any reviews yet!"):
        super().__init__(message)
        self.message = message

class NoUsersAvailableInPlatformException(Exception):
    def __init__(self, message="A minimum of 1 User must exist on Prentice. It seems like we don't have any users yet!"):
        super().__init__(message)
        self.message = message

class BadRequestException(Exception):
    def __init__(self, message="Bad request causing system to fail. Recheck your input."):
        super().__init__(message)
        self.message = message