from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email: EmailStr = 'user@gmail.com'
    password: str = 'qwerty'


class UserRespond(BaseModel):
    id: int
    email: EmailStr
    avatar: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
