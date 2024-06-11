# Library imports
import uvicorn
from http import HTTPStatus

from fastapi import (
    FastAPI,
    Request,
    Response,
    Depends,
    Body,
)

from fastapi.responses import (
    JSONResponse,
)
from fastapi.encoders import jsonable_encoder


from starlette.middleware.cors import CORSMiddleware

# Utility imports
from prentice_logger import logger

from src.utils.firebase import Client as firebaseClient

# Module imports
from src.account import controller as account
from src.company import controller as company
from src.review import controller as review
from src.salary import controller as salary
from src.utils.settings import ENV_TYPE

# Application
OPENAPI_URL = "/openapi.json" if ENV_TYPE == "DEV" else None

app = FastAPI(openapi_url=OPENAPI_URL)
firebase_client = firebaseClient

# Middlewares
# TODO add response ms counter - https://medium.com/@roy-pstr/fastapi-server-errors-and-logs-take-back-control-696405437983

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

# Register event handlers here
@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


# Global Exception Handlers
# https://fastapi.tiangolo.com/tutorial/handling-errors/
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content="Something went wrong."
    )


@app.get("/")
def root():
    return {
        "message": "Prentice API is up and running"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
