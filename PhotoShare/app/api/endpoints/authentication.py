from fastapi import APIRouter, Depends, BackgroundTasks, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi import status
from fastapi.security import HTTPAuthorizationCredentials

from PhotoShare.app.core.database import get_db
from PhotoShare.app.services.redis import RedisService as cache_redis                                            # noqa
from PhotoShare.app.services.roles import Roles
from PhotoShare.app.models.user import User
import PhotoShare.app.repositories.users as user_repo
from PhotoShare.app.schemas.user import (
    UserRespond, UserRegisterModel, UserLoginModel, TokenResponse
)
from PhotoShare.app.services.auth_service import (
        create_email_confirmation_token,
        send_in_background,
        get_email_form_confirmation_token,
        get_email_form_refresh_token,
        verify_password,
        oauth2_scheme,
        get_current_user
)
from PhotoShare.app.services.logout import add_token_to_revoked


router_auth = APIRouter(prefix="/auth", tags=["authentication / authorization"])


@router_auth.post("/signup", response_model=UserRespond, status_code=status.HTTP_201_CREATED,
                  summary='Створення користувача')
def signup(body: UserRegisterModel, background_task: BackgroundTasks,
           request: Request, session: Session = Depends(get_db)):
    """
    Функція реєстрації створює нового користувача в базі даних.
    Вона також надсилає користувачеві електронний лист із посиланням для підтвердження свого облікового запису.
    Функція повертає щойно створений об’єкт User.

    Args:
    body: UserModel: Валідація тіло запиту
    background_tasks: BackgroundTasks: Додавання завдання до черги фонових завдань
    request: Request: Отримання базову URL-адресу програми
    session: Session: Отримання сессії бази данних

    Returns: Об'єкт типу User
    """
    user = user_repo.create_user(body, session)
    token = create_email_confirmation_token({"email": user.email})
    background_task.add_task(send_in_background, user.email, str(request.base_url), token)
    return user


@router_auth.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK,
                  summary='Логінізація користувача')
def login(body: UserLoginModel, session: Session = Depends(get_db)):
    """
    Функція входу використовується для автентифікації користувача.
    Вона приймає адресу електронної пошти та пароль користувача як вхідні дані,
    перевіряє, чи є вони дійсними обліковими даними, і повертає токени (маркери) доступу.

    Args:
    body: UserModel: Отримання адресу електронної пошти та пароль із тіла запиту
    session: Session: Отримання сессії бази данних

    Returns:
    Токен (Маркер) доступу, токен (маркер) оновлення та тип авторизації
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='You are not authorized'
    )
    user, access_token, refresh_token = user_repo.user_login(body.email, session)                         # noqa
    if not verify_password(body.password, user.password):
        raise credential_exception
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router_auth.get("/refresh_token", response_model=TokenResponse, status_code=status.HTTP_200_OK,
                 summary="Отримати нові access та refresh_token")
def refresh_token(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
                  session: Session = Depends(get_db)):
    """
    Функція refresh_token використовується для оновлення токену(маркера) доступу.
    Функція приймає маркер оновлення (refresh_token) та повертає токен доступи (access_token) і тип авторизації.

    Args:
    credentials: HTTPAuthorizationCredentials: Отримання токену (refresh_token) із запиту
    db: Session: Передача сеанс бази даних у функцію

    Returns:
    Словник із access_token, refresh_token і token_type
    """
    token = token.credentials
    email = get_email_form_refresh_token(token)
    access_token, refresh_token = user_repo.refresh_token(email, token, session)                          # noqa
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router_auth.get("/email-confirmation/{token}", status_code=status.HTTP_200_OK,
                 summary='Встановлення користувача як confirmed')
def email_confirmation(token: str, session: Session = Depends(get_db)):
    """
    Функція email_confirmation використовується для підтвердження електронної адреси користувача.
    Також ми повертаємо об’єкт JSON, що містить «активацію»: «ваша електронна адреса підтверджена»

    Args:
    db: Session: Отримання сессії бази данних

    Returns:
    Словник з ключем "активація" та значенням "ваша електронна адреса підтверджена"
    """
    email = get_email_form_confirmation_token(token)
    user = user_repo.set_user_confirmation(email, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email token")
    return {'activation': 'you email is confirmed'}


@router_auth.get("/logout", summary="Виконання logout для авторизованного користувача")
def logout(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
                 user: User = Depends(get_current_user),
                 session: Session = Depends(get_db),
                 cache=Depends(cache_redis.get_redis)):
    """
    Функція logout використовується для відкликання access_token та refresh_token користувача.

    Args:
    token: Отримання
    cache: Отримання redis

    Returns:
    Словник з ще валідними відкликанними токенами
    """
    token = token.credentials
    token_revoked = add_token_to_revoked(token, cache=cache)
    user_repo.reset_refresh_token(user=user, session=session)
    return {'token_revoked': token}


@router_auth.patch("/banned/{email}", status_code=status.HTTP_200_OK, dependencies=[Depends(Roles(['admin']))])
def banned_user(email: str, session: Session = Depends(get_db)):
    """
    Функція banned_user використовується для встановлення заборони доступу до додатку певного користувача.

    Args:
    email: str: Отримання email користувача якому нам треба заборонити заходити в додаток
    session: Session: Отримання сессії бази данних

    Returns:
    json вівдповідь заборони користувача
    """
    user = user_repo.get_user_by_email(email=email, session=session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not found')
    user.banned = True
    user = user_repo.update_user(user, session)
    return {f'user {user.email}': 'BANNED'}
