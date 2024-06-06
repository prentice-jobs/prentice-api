# Library imports\
import uvicorn

from fastapi import (
    FastAPI,
)

from starlette.middleware.cors import CORSMiddleware

# Module imports
from src.account import controller as account
from src.company import controller as company
from src.review import controller as review
from src.salary import controller as salary
from src.utils.settings import ENV_TYPE

# Application
OPENAPI_URL = "/openapi.json" if ENV_TYPE == "DEV" else ""
app = FastAPI(openapi_url=OPENAPI_URL)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Add frontend origins here
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Authorization",
        "Cache-Control",
        "Content-Type",
        "DNT",
        "If-Modified-Since",
        "Keep-Alive",
        "Origin",
        "User-Agent",
        "X-Requested-With",
    ],
)

# Include routers after adding CORS middleware
app.include_router(account.account_router)
app.include_router(company.company_router)
app.include_router(review.review_router)
app.include_router(salary.salary_router)


@app.get("/")
def root():
    return {
        "message": "Prentice API is up and running"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
