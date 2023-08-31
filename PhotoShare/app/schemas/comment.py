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
    updated_at: List[datetime]
    #TODO
    #When the models for posts and users are finished must change the next two fields to correspond to them
    post: p.PostModel
    user: u.UserModel
    
    class Config:
        orm_mode = True