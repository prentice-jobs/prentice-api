from pydantic import EmailStr

class UserAlreadyExistsException(Exception):
    def __init__(self, user_email: EmailStr = "", message: str = "User already exists!"):
        if user_email:
            message = f"User ({user_email}) already exists!"

        # Instantiate base `Exception` object
        super(UserAlreadyExistsException, self).__init__(message)
        self.user_email = user_email

class RegistrationFailedException(Exception):
    def __init__(self, message="Error while registering new user"):
        super().__init__(message)
        self.message = message

class FirebaseTokenVerificationException(Exception):
    def __init__(self, message="Error while verifying JWT Token through Firebase Auth"):
        super().__init__(message)
        self.message = message