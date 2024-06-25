from fastapi import HTTPException


class CompanyNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Company not found")
