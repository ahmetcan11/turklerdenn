import os
from typing import List

import requests
import json
import random
import string
from fastapi import APIRouter, \
    Body, Depends, HTTPException, UploadFile, File, Form, Query
from google.cloud import storage


from fastapi.templating import Jinja2Templates


router = APIRouter()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'cert/fluent-horizon-388119-51be586f53a0.json'
templates = Jinja2Templates(directory="templates")

class GCStorage:
    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket_name = 'turkler_image_store'

    def upload_file(self, file):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        file_path = "profile/" + file.filename
        blob = bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type='image/jpeg')
        return f'https://storage.googleapis.com/{self.bucket_name}/{file_path}'


def upload_business_profile_image(business_name, images: List[UploadFile]):
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"business_profile_photos/{business_name}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_free_item_images(free_item_title: str, images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"free_item_photos/{free_item_title}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_event_images(event_title: str, images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"event_photos/{event_title}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_shared_room(room_title: str, images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"shared_room_photos/{room_title}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_house(house_title: str, images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"house_photos/{house_title}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_job(job_title: str, images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'

        image_urls = []
        for image in images:
            file_path = f"job_photos/{job_title}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def upload_general_images(images: List[UploadFile]) -> List[str]:
    try:
        storage_client = storage.Client.from_service_account_json('cert/fluent-horizon-388119-51be586f53a0.json')
        bucket_name = 'turkler_image_store'
        characters = string.ascii_letters + string.digits  # You can add more characters if needed
        # Generate a random string of the specified length
        random_string = ''.join(random.choice(characters) for _ in range(7))
        image_urls = []
        for image in images:
            file_path = f"general_photos/{random_string}/{image.filename}"
            # Upload the file to Google Cloud Storage
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_path)
            blob.upload_from_file(image.file)

            image_urls.append(f'https://storage.googleapis.com/{bucket_name}/{file_path}')

        return image_urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
