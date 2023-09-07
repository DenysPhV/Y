from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserLoginModel(BaseModel):
    email: EmailStr = 'user@gmail.com'
    password: str = 'qwerty'
    username: str


class UserRegisterModel(BaseModel):
    email: EmailStr = 'user@gmail.com'
    password: str = 'qwerty'
    username: str
    first_name: str
    last_name: str


class UserProfileModel(BaseModel):
    email: EmailStr
    first_name: str | None
    last_name: str | None
    username: str | None
    created_at: datetime
    avatar: str
    uploaded_photos: int


class UserRespond(BaseModel):
    id: int
    username: str
    email: EmailStr
    username: str | None
    first_name: str | None
    last_name: str | None
    uploaded_photos: int
    avatar: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserUsername(BaseModel):
    username: str


class UserFirstname(BaseModel):
    first_name: str


class UserLastname(BaseModel):
    last_name: str
