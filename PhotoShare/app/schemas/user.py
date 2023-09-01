from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    email: EmailStr
    password: str


class UserRespond(BaseModel):
    id: int
    email: EmailStr
    avatar: str

