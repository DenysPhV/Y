from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi import status

from PhotoShare.app.schemas.user import UserModel, UserRespond
from PhotoShare.app.core.database import get_db
from PhotoShare.app.models.user import User
import PhotoShare.app.repositories.users as user_repo
from PhotoShare.app.services.auth_service import create_email_confirmation_token, send_in_background, \
    get_email_form_confirmation_token

router_auth = APIRouter(prefix="/auth")


@router_auth.post("/signup", response_model=UserRespond, status_code=status.HTTP_201_CREATED, summary='create user')
async def signup(body: UserModel, background_task: BackgroundTasks, request: Request, session: Session = Depends(get_db)):
    user = await user_repo.create_user(body, session)
    token = await create_email_confirmation_token({"email": user.email})
    background_task.add_task(send_in_background, user.email, str(request.base_url), token)
    return user


@router_auth.get("/email-confirmation/{token}", status_code=status.HTTP_200_OK)
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
