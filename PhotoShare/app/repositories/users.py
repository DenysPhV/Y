import asyncio

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from PhotoShare.app.models.user import User
from PhotoShare.app.schemas.user import UserModel
from PhotoShare.app.services.auth_service import get_password_hash, create_access_token, create_refresh_token

from PhotoShare.app.services.auth_service import get_current_user


async def get_user_by_email(email: str, session: Session):
    user = session.query(User).filter_by(email=email).first()
    return user


async def create_user(body: UserModel, session: Session):
    is_db_full = session.query(User).first()
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        raise err
    user = await get_user_by_email(body.email, session)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User exists already')
    hashed_password = get_password_hash(password=body.password)
    user = User(email=body.email, password=hashed_password, avatar=avatar)
    if not is_db_full:
        user.role = 'admin'
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


async def user_login(email: str, session: Session):
    access_token = None
    refresh_token = None
    user = await get_user_by_email(email, session)
    if user:
        access_token = await create_access_token(data={"email": user.email})
        refresh_token = await create_refresh_token(data={"email": user.email})
        user.refresh_token = refresh_token
        session.commit()
    return user, access_token, refresh_token


async def reset_refresh_token(user, session: Session):
    user.refresh_token = None
    session.commit()


async def refresh_token(email: str, token: str, session: Session):
    """
    The refresh_token function is used to refresh the access token.
    It takes in an email and a refresh token, then checks if the user exists and if their
    refresh_token matches what was passed in. If it does not match, we set their refresh_token to None
    and raise an HTTPException with status code 401 (Unauthorized). If it does match, we create a new
    access token using the create_access_token function from fastapi-users' utils module. We also generate
    a new refresh token using the same method as before. Then we update our database with this new information.

    Args:
    email: str: Get the user email
    token: str: Get the token from the request
    db: Session: Pass the database session to the function

    Returns:
    The access_token and refresh_token
    """
    user = await get_user_by_email(email, session)
    if user.refresh_token != token:
        await reset_refresh_token(user=user, session=session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"email": user.email})
    refresh_token = await create_refresh_token(data={"email": user.email})  # noqa
    user.refresh_token = refresh_token
    session.commit()
    return access_token, refresh_token
