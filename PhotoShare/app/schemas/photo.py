from datetime import datetime

from pydantic import BaseModel, Field

from PhotoShare.app.schemas.user import UserRespond


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    id: int

    class Config:
        orm_mode = True


class PhotoModel(BaseModel):
    name: str = Field(max_length=150, min_length=3)
    description: str = Field(max_length=300, min_length=3)
    # tags: list = Field(max=5)


class PhotoUpdate(PhotoModel):
    description: str = Field(max_length=300)
    photo_url: str
    updated_at: datetime | None


class PhotoResponse(PhotoModel):
    id: int = 1
    photo_url: str
    created_at: datetime | None
    updated_at: datetime | None
    user: UserRespond | None
    rating: int = 0

    class Config:

        from_attributes = True


