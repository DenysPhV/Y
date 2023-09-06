from datetime import datetime, timedelta
from pathlib import Path

from passlib.context import CryptContext
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError                                                                                  # noqa
from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi_mail.errors import ConnectionErrors
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from PhotoShare.app.core.config import settings
from PhotoShare.app.core.database import get_db
from PhotoShare.app.services.redis import RedisService as redis_cache                                           # noqa
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
    Функція verify_password приймає як аргументи простий текстовий пароль і хешований пароль.
    Потім він використовує об’єкт pwd_context, щоб перевірити, чи збігається простий текстовий пароль із хешованим
    пароль.

    Args: hashed_password: збережений хешований пароль із бази даних

    Returns:
    Логічне значення перевірки на відповідність паролів
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """
    Функція get_password_hash приймає пароль як аргумент і повертає хешовану версію цього пароля.

    Args: password: str: Передавача пароля, який потрібно хешувати

    Returns:
    Хешований пароль
    """
    return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: float | None = None):
    """
    Функція create_access_token створює маркер JWT, який використовується для автентифікації користувача.
    Функція приймає два аргументи: дані та expires_delta. Аргумент даних - це словник, що містить адресу електронної
    пошти. Аргумент expires_delta визначає тривалість дії маркера.

    Args:
    data: dict: Передача email, який ми хочемо закодувати у наш jwt
    expires_delta: float: Встановлення термін дії маркера доступу

    Returns:
    Веб-токен json (jwt), який містить ідентифікатор користувача
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
    Функція create_refresh_token створює маркер оновлення для користувача.

    Args:
    data: dict: Передайте дані, які ми хочемо закодувати в наш jwt
    expires_delta: float: Встановлення термін дії маркера

    Returns:
    Маркер оновлення
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
    Функція create_email_confirmation_token створює маркер JWT, який використовується для підтвердження електронної
    адреси користувача.Функція приймає два аргументи: дані та expires_delta. Аргумент даних - це словник, що містить
    дані користувача адреса електронної пошти, ім’я користувача та хеш пароля (хеш пароля буде використано для входу
    після підтвердження електронної пошти).
    Аргумент expires_delta є необов’язковим значенням із плаваючою точкою, яке вказує, скільки часу має закінчитися
    термін дії маркера (у секундах). Якщо значення expires_delta не вказано, за замовчуванням воно становить 5 хвилин.

    Args:
    data: dict: Передайте дані, які ми хочемо закодувати в наш jwt
    expires_delta: float: Встановлення термін дії маркера

    Returns:
    Токен для підтвердження елетронної скриньки
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
                           session: Session = Depends(get_db), cache=Depends(redis_cache.get_redis)):
    """
    Функція get_current_user — це залежність, яка використовуватиметься в
    для отримання поточного користувача. Вона приймає додатковий параметр маркера, який
    передається Depends(oauth2_scheme). Схема oauth2 повертає об’єкт типу
    HTTPAuthorizationCredentials, який містить JWT.

    Args:
    token: HTTPAuthorizationCredentials: Отримайте маркер jwt із заголовка з поля "авторизація"
    session: Session: Сессія для роботи з базою даних
    cache: Redis: Редіс кліент для роботи з кешом

    Returns:
    Об’єкт користувача, який є моделлю користувача
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
            detail='You are not authorizated'
        )
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_ACCESS_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.query(User).filter_by(email=email).first()
    return user


async def send_in_background(email: str, host: str, token: str):
    """
    Функція send_in_background — це співпрограма, яка надсилає електронний лист на адресу електронної пошти користувача.

    Args:
    email: str: Передача електронної адреси одержувача
    host: str: Передача host для даного сайту
    token: str: Передача маркеру до шаблону електронної пошти

    Returns:
    Об'єкто співпрограмми
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
    Функція get_email_form_confirmation_token приймає маркер як аргумент.
    Потім вона намагається декодувати маркер за допомогою SECRET_EMAIL_KEY і ALGORITHM.
    У разі успіху повертається адреса електронної пошти яка закодована в маркері.
    В іншому випадку, якщо виникає помилка JWTError, виникає HTTPException із кодом статусу 401 (неавторизовано) та
    детальним повідомленням «Не вдалося перевірити облікові дані».

    Args:
    token: str: Отримання маркера з url

    Returns:
    Адреса електронної пошти, пов’язана з маркером
    """
    try:
        payload = jwt.decode(token, SECRET_EMAIL_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


def get_email_form_refresh_token(refresh_token: str):
    """
    Функція get_email_form_refresh_token приймає маркер оновлення (refresh_token) як аргумент і повертає пов’язану
    електронну адресу з цим маркером оновлення. Він робить це шляхом декодування JWT за допомогою SECRET_REFRESH_KEY,
    який зберігається в config.py.

    Args:
    refresh_token: str: Передайте маркер оновлення, надісланий клієнтом headers в полі Authorization

    Returns:
    Електронна адреса користувача, який намагається оновити маркер доступу
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_REFRESH_KEY, algorithms=[ALGORITHM])
        email = payload.get('email')
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
