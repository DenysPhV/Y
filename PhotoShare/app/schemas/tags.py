from pydantic import BaseModel


class NewTagModel(BaseModel):
    photo_id : int
    tag: str
