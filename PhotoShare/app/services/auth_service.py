from datetime import datetime, timedelta
from pathlib import Path

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi_mail.errors import ConnectionErrors
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from PhotoShare.app.core.config import settings
from PhotoShare.app.core.database import get_db, get_redis
from PhotoShare.app.models.user import User
from PhotoShare.app.services.logout import (
    get_revoked_tokens,
    get_key_from_token,
    get_valid_token_from_revoked
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_ACCESS_KEY = settings.secret_access_key
SECRET_REFRESH_KEY = settings.secret_refresh_key
SECRET_EMAIL_KEY = settings.secret_email_key
ALGORITHM = settings.algorithm

oauth2_scheme = HTTPBearer()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.email_username,
    MAIL_PASSWORD=settings.email_password,
    MAIL_FROM=settings.email_from,
    MAIL_PORT=settings.email_port,
    MAIL_SERVER=settings.email_server,
    MAIL_FROM_NAME=settings.email_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


def verify_password(plain_password, hashed_password):

    """
    The verify_password function takes a plain-text password and a hashed password as arguments.
    It then uses the pwd_context object to verify that the plain-text password matches the hashed
    password.

    Args:
    hashed_password: Store the hashed password from the database

    Returns:
    A boolean value
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):

    """
    The get_password_hash function takes a password as an argument and returns the hashed version of that password.

    Args:
    password: str: Pass the password that is to be hashed

    Returns:
    A hash of the password
    """
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: float | None = None):
    """
    The create_access_token function creates a JWT token that is used to authenticate the user.
    The function takes in two arguments: data and expires_delta. The data argument is a dictionary containing the
    user's id, username, email address and role (admin or user). The expires_delta argument specifies how long the token will be valid for.

    Args:
    data: dict: Pass the data we want to encode in our jwt
    expires_delta: Optional[float]: Set the expiration time of the access token

    Returns:
    A json web token (jwt) that contains the user's id,
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_ACCESS_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: float | None = None):
    """
    The create_refresh_token function creates a refresh token for the user.

    Args:
    data: dict: Pass in the data that we want to encode into our jwt
    expires_delta: float: Set the expiration time for the token

    Returns:
    A refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    encoded_refresh_token = jwt.encode(to_encode, SECRET_REFRESH_KEY, algorithm=ALGORITHM)
    return encoded_refresh_token


async def create_email_confirmation_token(data: dict, expires_delta: float | None = None):
    """
    The create_email_confirmation_token function creates a JWT token that is used to confirm the user's email address.
    The function takes in two arguments: data and expires_delta. The data argument is a dictionary containing the user's
    email address, username, and password hash (the password hash will be used to log in after confirming their email).
    The expires_delta argument is an optional float representing how long until the token should expire (in seconds). If no
    expires_delta value is provided, then it defaults to 1 minute.

    Args:
    data: dict: Pass in the user's email address and username
    expires_delta: float: Set the expiration time of the token

    Returns:
    A jwt token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=5)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_EMAIL_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
                           session: Session = Depends(get_db), cache=Depends(get_redis)):
    """
    The get_current_user function is a dependency that will be used in the
    get_current_active_user endpoint. It takes an optional token parameter, which
    is passed by Depends(oauth2_scheme). The oauth2 scheme returns an object of type
    HTTPAuthorizationCredentials, which contains the JWT in its credentials attribute.

    Args:
    token: HTTPAuthorizationCredentials: Get the jwt token from the authorization header
    db: Session: Access the database

    Returns:
    A user object, which is a user model
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = token.credentials
    tokens_revoked_all = await get_revoked_tokens(cache=cache)
    tokens_revoked_valid = await get_valid_token_from_revoked(tokens_revoked_all, cache=cache)

    if await get_key_from_token(token) in tokens_revoked_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='YOUR TOKEN HAS BEEN REVOKE'
        )
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_ACCESS_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception
    user = session.query(User).filter_by(email=email).first()
    return user


async def send_in_background(email: str, host: str, token: str):
    """
    The send_in_background function is a coroutine that sends an email to the user's email address.
    It takes in three arguments:
    -email: The user's email address, which will be used as the recipient of the message.
    -host: The hostname of your website

    Args:
    email: str: Specify the email address of the recipient
    token: str: Pass the token to the email template

    Returns:
    A coroutine object
    """
    try:
        message = MessageSchema(
            subject="Email Confirmation",
            recipients=[email],
            template_body={"email": email, 'host': host, "token": token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_page.html")
    except ConnectionErrors as err:
        print(err)


def get_email_form_confirmation_token(token: str):
    """
    The get_email_form_confirmation_token function takes in a token as an argument.
    It then tries to decode the token using the SECRET_EMAIL_KEY and ALGORITHM.
    If it is successful, it returns the email address that was encoded into the token.
    Otherwise, if there is a JWTError, it raises an HTTPException with status code 401 (Unauthorized) and detail message 'Could not validate credentials'.

    Args:
    token: str: Get the token from the url

    Returns:
    The email address associated with the token
    """
    try:
        payload = jwt.decode(token, SECRET_EMAIL_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


def get_email_form_refresh_token(refresh_token: str):
    """
    The get_email_form_refresh_token function takes a refresh token as an argument and returns the email associated with that refresh token.
    It does this by decoding the JWT using the SECRET_REFRESH_KEY, which is stored in config.py.

    Args:
    refresh_token: str: Pass in the refresh token that was sent by the client

    Returns:
    The email of the user who is trying to refresh the access token
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_REFRESH_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')