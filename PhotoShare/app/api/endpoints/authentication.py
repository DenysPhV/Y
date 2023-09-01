from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi import status

from PhotoShare.app.schemas.user import UserModel, UserRespond, LoginResponse
from PhotoShare.app.core.database import get_db
from PhotoShare.app.models.user import User
import PhotoShare.app.repositories.users as user_repo
from PhotoShare.app.services.auth_service import (
    create_email_confirmation_token,
    send_in_background,
    get_email_form_confirmation_token,
    verify_password,
)
from PhotoShare.app.services.roles import Roles

router_auth = APIRouter(prefix="/auth", tags=["autentication/authorization"])


@router_auth.post("/signup", response_model=UserRespond, status_code=status.HTTP_201_CREATED, summary='create user')
async def signup(body: UserModel, background_task: BackgroundTasks,
                 request: Request, session: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    It also sends an email to the user with a link to confirm their account.
    The function returns the newly created User object.

    Args:
    body: UserModel: Validate the request body
    background_tasks: BackgroundTasks: Add a task to the background tasks queue
    request: Request: Get the base url of the application
    db: Session: Get the database session

    Returns:
    The user object
    """
    user = await user_repo.create_user(body, session)
    token = await create_email_confirmation_token({"email": user.email})
    background_task.add_task(send_in_background, user.email, str(request.base_url), token)
    return user


@router_auth.post("/login", response_model= LoginResponse, status_code=status.HTTP_200_OK, summary='login user')
async def login(body: UserModel, session: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the email and password of the user as input,
    checks if they are valid credentials, and returns an access token.

    Args:
    body: UserModel: Get the email and password from the request body
    db: Session: Get the database session

    Returns:
    An access token and a refresh token
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='You are not authorized'
    )
    user, access_token, refresh_token = await user_repo.user_login(body.email, session)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Your email not confirmed')
    if not verify_password(body.password, user.password):
        raise credential_exception
    return {'email': user.email, "access_token": access_token, "refresh_token": refresh_token}


@router_auth.get("/email-confirmation/{token}", status_code=status.HTTP_200_OK, summary='set user as authenticated')
async def email_confirmation(token: str, session: Session = Depends(get_db)):
    """
    The email_confirmation function is used to confirm a user's email address.
    Otherwise, we return a JSON object containing 'activation': 'you email is confirmed'

    Args:
    db: Session: Get the database session

    Returns:
    A dictionary with a key of activation and a value of you email is confirmed
    """
    email = get_email_form_confirmation_token(token)
    user = await user_repo.set_user_confirmation(email, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email token")
    return {'activation': 'you email is confirmed'}
