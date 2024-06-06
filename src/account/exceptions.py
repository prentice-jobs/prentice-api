from pydantic import EmailStr

class UserAlreadyExistsException(Exception):
    def __init__(self, message: str, user_email: EmailStr):
        if message is None:
            # Useful default error message
            if user_email:
                message = f"User ({user_email}) already exists!"
            else:
                message = "User already exists!"

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