from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email: EmailStr = 'mail@service.ext'
    password: str = 'some password'


class UserRespond(BaseModel):
    id: int
    email: EmailStr
    avatar: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
