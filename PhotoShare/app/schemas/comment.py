from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from PhotoShare.app.schemas import photo as p
from PhotoShare.app.schemas import user as u


class CommentModel(BaseModel):
    content: str = Field(max_length=265)


class CommentResponse(CommentModel):
    id: int
    created_at: datetime
    updated_at: List[datetime] | None
    user_id: int
    photo_id: int

    class Config:
        orm_mode = True
