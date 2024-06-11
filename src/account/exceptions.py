from pydantic import EmailStr
from fastapi import HTTPException
from http import HTTPStatus

class UserAlreadyExistsException(Exception):
    def __init__(self, user_email: EmailStr = "", message: str = "User already exists!"):
        if user_email:
            message = f"User ({user_email}) already exists!"

        # Instantiate base `Exception` object
        super(UserAlreadyExistsException, self).__init__(message)
        self.user_email = user_email

class UnauthorizedOperationException(Exception):
    def __init__(self, message="Unauthorized operation. You may have to log in with the necessary permissions to perform this action."):
        super().__init__(message)
        self.message = message

class RegistrationFailedException(Exception):
    def __init__(self, message="Error while registering new user"):
        super().__init__(message)
        self.message = message

class FirebaseTokenVerificationException(HTTPException):
    def __init__(
        self, 
        detail="Error while verifying JWT Token through Firebase Auth",
        status_code=HTTPStatus.UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"}
    ):
        super().__init__(detail, status_code, headers)
        # self.message = message
        self.detail = detail
        self.status_code = status_code
        self.headers = headers