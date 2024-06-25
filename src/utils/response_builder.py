from http import HTTPStatus
import uuid

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# from controller.context_manager import context_api_id, context_log_meta
from logger import logger
from src.core.schema import GenericAPIResponseModel

def build_api_response(generic_response: GenericAPIResponseModel) -> JSONResponse:
    try:
        if not generic_response.status:
            if not generic_response.error:
                generic_response.status = HTTPStatus.OK
            else:
                generic_response.status = HTTPStatus.UNPROCESSABLE_ENTITY
        
        response_content_json = jsonable_encoder(generic_response)

        logger.info(msg=f"build_api_response: Succesfully generated response with status code {generic_response.status}")
        
        return JSONResponse(
            status_code=generic_response.status,
            content=response_content_json,
        )
    except Exception as exc:
        logger.error(msg=f"Exception occuring in build_api_response: {exc}")
        
        return JSONResponse(
            status_code=generic_response.status or 500,
            content=generic_response.error or "Error while building API Response.",
        )