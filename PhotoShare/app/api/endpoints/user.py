import hashlib

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from PhotoShare.app.models.user import User
from PhotoShare.app.services.auth_service import get_current_user
from PhotoShare.app.schemas.user import UserRespond, UserFirstname, UserLastname, UserProfileModel
from PhotoShare.app.core.database import get_db
from PhotoShare.app.repositories.users import update_user, get_user_by_email

router_user = APIRouter(prefix="/user", tags=["user"])


@router_user.get("/profile/{email}", response_model=UserProfileModel, status_code=status.HTTP_200_OK)
async def get_user_profile(email: str, session: Session = Depends(get_db)):
    user = await get_user_by_email(email=email, session=session)
    return {
        'user_email': user.email,
        'user_first_name': user.first_name,
        'user_last_name': user.last_name,
        'user_username': user.username,
        'created_at': user.created_at,
        'avatar': user.avatar,
        'images_uploaded': user.uploaded_photos
    }


@router_user.get("/me", response_model=UserRespond, status_code=status.HTTP_200_OK,
                 summary='Отримати інформацію про користувача')
async def me(user: User = Depends(get_current_user)):
    return user


@router_user.patch("/edit/username/{username}", response_model=UserRespond, status_code=status.HTTP_200_OK)
async def change_username(username: str, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    user.username = username
    user = await update_user(user, session)
    return user


@router_user.patch("/edit/firstname/{firstname}", response_model=UserRespond, status_code=status.HTTP_200_OK)
async def edit_firstname(body: UserFirstname, user: User = Depends(get_current_user),
                         session: Session = Depends(get_db)):
    user.first_name = body.first_name
    user = await update_user(user, session)
    return user


@router_user.patch("/edit/lastname/{lastname}", response_model=UserRespond, status_code=status.HTTP_200_OK)
async def edit_lastname(body: UserLastname, user: User = Depends(get_current_user),
                        session: Session = Depends(get_db)):
    user.last_name = body.last_name
    user = await update_user(user, session)
    return user


@router_user.patch("/edit/avatar", response_model=UserRespond, status_code=status.HTTP_200_OK)
async def upload_avatar(file: UploadFile = File(), user: User = Depends(get_current_user),
                        session: Session = Depends(get_db)):
    ...
    public_id = f"Y/{user.email}/avatar/" + hashlib.sha256(file.filename.encode()).hexdigest()[:10]
    image = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill',
                                                          version=image.get('version'))
    user.avatar = url
    user = await update_user(user, session)
    return user


