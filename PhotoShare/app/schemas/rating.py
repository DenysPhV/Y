from pydantic import BaseModel, Field

class RatingModel(BaseModel):
    rating: int

class RatingResponse(RatingModel):
    id: int
    user_id: int
    photo_id: int