import hashlib

import cloudinary
import cloudinary.uploader

from PhotoShare.app.core.config import settings


class CloudinaryService:

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def get_public_id(filename: str) -> str:
        public_id = hashlib.sha256(filename.encode()).hexdigest()[:10]
        return f"avatars/{public_id}"

    @staticmethod
    def upload_avater(file, public_id):
        image = cloudinary.uploader.upload(file, public_id=public_id)
        return image

    @staticmethod
    def get_avatar(public_id: str, version: str) -> str:
        url = cloudinary.CloudinaryImage(public_id).build_url(width=200, height=200, crop='fill', version=version)
        return url
