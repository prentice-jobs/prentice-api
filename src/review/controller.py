from fastapi import (
  APIRouter,
  Request,
  Response,
  Depends,
  Body
)

from enum import Enum

VERSION = "v1"
ENDPOINT = "review"

review_router = APIRouter(
  prefix=f"/{VERSION}/{ENDPOINT}",
  tags=[ENDPOINT]
)
