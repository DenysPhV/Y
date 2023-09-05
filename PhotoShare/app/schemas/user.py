from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email: EmailStr = 'user@gmail.com'
    password: str = 'qwerty'
    username: str
    first_name: str
    last_name: str


class UserRespond(BaseModel):
    id: int
    email: EmailStr
    username: str | None
    first_name: str | None
    last_name: str | None
    uploaded_photos: int
    avatar: str



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
