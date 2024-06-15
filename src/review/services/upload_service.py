from pydantic import UUID4
from fastapi import UploadFile
from http import HTTPStatus


from google.cloud import storage

from prentice_logger import logger
from src.core.schema import GenericAPIResponseModel

from src.review.constants import messages as ReviewMessages

from src.utils.settings import (
    GCS_BUCKET_OFFER_LETTER,
    GCS_BUCKET_STOPWORDS,
)

class UploadService:
    def __init__(self) -> None:
        self.client = storage.Client()
        self.offer_letter_bucket = GCS_BUCKET_OFFER_LETTER
        self.stopwords_bucket = GCS_BUCKET_STOPWORDS
        
    def upload_file(self, file: UploadFile, user_id: UUID4) -> GenericAPIResponseModel:
        try:
            bucket = self.client.get_bucket(self.offer_letter_bucket)
        
            file_path = self.construct_file_path(user_id=user_id, file_name=file.filename)
            blob =  bucket.blob(file_path)
            blob.upload_from_file(file.file, content_type="image/jpeg")

            url = f"https://storage.cloud.google.com/{self.offer_letter_bucket}/{file_path}"
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.CREATED,
                message=ReviewMessages.GCS_OBJECT_CREATE_SUCCESS,
                data=url
            )

            return response
        except Exception as err:
            logger.error(f"Unknown exception while uploading file: {err.__str__()}")
            
            response = GenericAPIResponseModel(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=ReviewMessages.GCS_OBJECT_CREATE_FAILED,
                error=ReviewMessages.GCS_OBJECT_CREATE_FAILED,
            )

            return response
        
    def fetch_stopwords_array(self):
        blob_name = "stopwords.txt"

        bucket = self.client.get_bucket(self.stopwords_bucket)
        blob = bucket.blob(blob_name)
        
        stopwords_array = []
    
        with blob.open("r") as f:
            for line in f:
                stopwords_array.append(line.strip())
        
        return stopwords_array



    def construct_file_path(self, user_id: UUID4, file_name: str) -> str:
        return f"{str(user_id)}/{file_name}"