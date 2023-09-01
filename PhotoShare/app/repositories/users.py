import asyncio

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from PhotoShare.app.models.user import User
from PhotoShare.app.schemas.user import UserModel
from PhotoShare.app.services.auth_service import get_password_hash


async def get_user_by_email(email: str, session: Session):
    user = session.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, session: Session):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        ...

    user = await get_user_by_email(body.email, session)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User exists already')
    hashed_password = get_password_hash(password=body.password)
    user = User(email=body.email, password=hashed_password, avatar=avatar)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def set_user_confirmation(email: str, db: Session):
    """
    The set_user_confirmation function sets the user's confirmation status to True.

    Args:
    email: str: Get the user by email
    db: Session: Pass the database session to the function

    Returns:
    The user object
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        db.commit()
    return user


