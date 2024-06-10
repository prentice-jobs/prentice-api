from pydantic import UUID4
from fastapi import UploadFile
from http import HTTPStatus


from google.cloud import storage


from src.core.schema import GenericAPIResponseModel

from src.review.constants import messages as ReviewMessages

from src.utils.settings import (
    GCS_BUCKET_PRENTICE
)

class UploadService:
    def __init__(self) -> None:
        self.client = storage.Client()
        self.bucket_name = GCS_BUCKET_PRENTICE
        
    def upload_file(self, file: UploadFile, user_id: UUID4) -> GenericAPIResponseModel:
        bucket = self.client.get_bucket(self.bucket_name)
        
        file_path = self.construct_file_path(user_id=user_id, file_name=file.filename)
        blob =  bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type="image/jpeg")

        url = f"https://storage.cloud.google.com/{self.bucket_name}/{file_path}"
        
        return GenericAPIResponseModel(
            status=HTTPStatus.CREATED,
            message=ReviewMessages.GCS_OBJECT_CREATE_SUCCESS,
            data=url
        )

    def construct_file_path(self, user_id: UUID4, file_name: str) -> str:
        return f"{str(user_id)}/{file_name}"