import pickle

from pydantic import UUID4
from fastapi import UploadFile
from http import HTTPStatus
from typing import List
import math
import string

from google.cloud import storage

from prentice_logger import logger
from src.core.schema import GenericAPIResponseModel
from src.review.constants import messages as ReviewMessages
from src.utils.settings import (
    GCS_BUCKET_OFFER_LETTER,
    GCS_BUCKET_STOPWORDS,
    GCS_BUCKET_RECSYS,
)

class CloudStorageService:
    def __init__(self) -> None:
        self.client = storage.Client()
        self.offer_letter_bucket = GCS_BUCKET_OFFER_LETTER
        self.stopwords_bucket = GCS_BUCKET_STOPWORDS
        self.recsys_bucket = GCS_BUCKET_RECSYS
        self.vectorizer = None
        
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

    def fetch_stopwords_array(self) -> List[str]:
        blob_name = "stopwords.txt"

        try:
            bucket = self.client.get_bucket(self.stopwords_bucket)
            blob = bucket.blob(blob_name)
        
            stopwords_array = []
    
            with blob.open("r") as f:
                for line in f:
                    stopwords_array.append(line.strip())
        
            return stopwords_array
        except Exception as err:
            logger.error(f"Error while fetching stopwords array: {err}")
            return []
        
    def fetch_recsys_vectorizer(self):
        blob_name = "vectorizer.pkl"

        # Check vectorizer object in cache to reduce remote calls
        if self.vectorizer is not None:
            return self.vectorizer

        try:
            bucket = self.client.get_bucket(self.recsys_bucket)
            blob = bucket.blob(blob_name)

            # Caches vectorizer in-memory
            vectorizer_data = blob.download_as_bytes()
            self.vectorizer = pickle.loads(vectorizer_data)

            return self.vectorizer
        except Exception as err:
            logger.error(f"Unknown error while loading RecSys vectorizer: {err.__str__()}")
            
            return None
    
    def keyword_extractor(self, input_strings: List[str], company_name: str) -> List[str]:
        try:
            stop_words = self.fetch_stopwords_array()
            company_words = company_name.split()

            stop_words = set(stop_words)
            stop_words.update(company_words)

            def compute_tf(document):
                word_count = {}
                tf_dict = {}
                total_words = 0

                for word in document.split():
                    word = word.lower().strip(string.punctuation)
                    if word not in stop_words:
                        if word not in word_count:
                            word_count[word] = 0
                        word_count[word] += 1
                        total_words += 1

                for word, count in word_count.items():
                    tf_dict[word] = count / total_words
                return tf_dict

            document_tfs = [compute_tf(doc) for doc in input_strings]

            idf_dict = {}
            total_documents = len(input_strings)
            all_words = set()

            for tf in document_tfs:
                all_words.update(tf.keys())

            for word in all_words:
                count = sum(1 for tf in document_tfs if word in tf)
                idf_dict[word] = math.log(total_documents / count)

            tf_idf = [{word: tf[word] * idf_dict[word] for word in tf} for tf in document_tfs]

            average_tf_idf = {}
            for word in all_words:
                total_tf_idf = sum(doc.get(word, 0) for doc in tf_idf)
                average_tf_idf[word] = total_tf_idf / total_documents

            sorted_average_tf_idf = sorted(average_tf_idf.items(), key=lambda item: item[1], reverse=True)[:4]

            return [word for word, _ in sorted_average_tf_idf]

        except Exception as err:
            logger.error(f"Error in keyword_extractor: {err}")
            return []

    def construct_file_path(self, user_id: UUID4, file_name: str) -> str:
        return f"{str(user_id)}/{file_name}"