from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr

from PhotoShare.app.schemas.user import UserRespond


class PhotoModel(BaseModel):
    name: str = Field(max_length=150, min_length=3)
    description: str = Field(max_length=300, min_length=3)
    photo_url: str


class PhotoUpdate(PhotoModel):
    description: str = Field(max_length=300)
    photo_url: str
    updated_at: datetime | None


class PhotoResponse(PhotoModel):
    id: int = 1
    created_at: datetime | None
    updated_at: datetime | None
    user: UserRespond | None

    class Config:
        orm_mode = True

