from datetime import datetime

from fastapi import Form, UploadFile
from pydantic import BaseModel, Field

from PhotoShare.app.schemas.user import UserPhotoRespond, UserRespond


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class CreateModelPhoto(BaseModel):
    name: str = Form(...)
    description: str = Form(...)
    file: UploadFile = Form(...)


class PhotoModel(BaseModel):
    name: str = Field(max_length=150, min_length=3)
    description: str = Field(max_length=300, min_length=3)
    # tags: list = Field(max=5)


class PhotoUpdate(PhotoModel):
    ...


class PhotoResponse(PhotoModel):
    id: int = 1
    photo_url: str
    created_at: datetime | None
    updated_at: datetime | None
    user: UserPhotoRespond | None
    rating: int = 0
    tags: list[TagModel]

    class Config:
        from_attributes = True
