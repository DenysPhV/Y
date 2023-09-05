from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from libgravatar import Gravatar

from PhotoShare.app.models.user import User
from PhotoShare.app.schemas.user import UserModel
from PhotoShare.app.services.auth_service import get_password_hash, create_access_token, create_refresh_token


async def get_user_by_email(email: str, session: Session):
    """
    Функція get_user_by_email приймає електронний лист і сеанс,
    і повертає користувача з цією електронною поштою. Якщо такого користувача не існує, повертається None.

    Args:
    email: str: Вказуємо email користувача, якого ми хочемо отримати
    session: Session: Передаємо об’єкт сеансу функції

    Returns:
    Об’єкт користувача, який відповідає наданій адресі електронної пошти
    """
    user = session.query(User).filter_by(email=email).first()
    return user


async def update_user(user: User, session: Session):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def create_user(body: UserModel, session: Session):
    """
    Функція create_user створює нового користуваа в базі данних

    Args:
    email: str: Вказуємо email і пароль в body запиту користувача, якого ми хочемо створити
    session: Session: Передаємо об’єкт сеансу функції

    Returns:
    Об'єкт класу User користувача якаго ми створили в базі даних
    """
    is_db_full = session.query(User).first()
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
    user.username = None if body.username == "string" else body.username
    user.username = None if body.first_name == "string" else body.first_name
    user.username = None if body.last_name == "string" else body.last_name
    await update_user(user, session)
    return user


async def set_user_confirmation(email: str, session: Session):
    """
    Функція set_user_confirmation встановлює для статусу підтвердження користувача значення True.

    Args:
    email: str: Email користувача
    session: Session: Передача сеанса бази даних у функцію

    Returns:
    Об'єкт користувача
    """
    user = await get_user_by_email(email, session)
    if user:
        user.confirmed = True
        session.commit()
    return user


async def user_login(email: str, session: Session):
    """
    Функція user_login вибирає користуваа з бази даних, email якого ми передали як аргумент у ф-цію. Створює access та
    refresh токени

    Args:
    email: str: Email користувача
    session: Session: Передача сеанса бази даних у функцію

    Returns:
    Об'єкт користувача, access та refresh_token
    """
    access_token = None
    refresh_token = None                                                                                        # noqa
    user = await get_user_by_email(email, session)
    if user:
        access_token = await create_access_token(data={"email": user.email})
        refresh_token = await create_refresh_token(data={"email": user.email})                                  # noqa
        user.refresh_token = refresh_token
        session.commit()
    return user, access_token, refresh_token


async def reset_refresh_token(user, session: Session):
    """
    Функція reset_refresh_token скидає значення поля refresh_token в базі данних

    Args:
    user: User: об'єкт користувача
    session: Session: Передача сеанса бази даних у функцію

    Returns:
    співпрограмму для виконання в EventLoop
    """
    user.refresh_token = None
    session.commit()


async def refresh_token(email: str, token: str, session: Session):
    """
    Функція refresh_token використовується для оновлення маркера доступу.
    Вона приймає електронний лист і маркер оновлення, а потім перевіряє, чи існує користувач і чи
    refresh_token відповідає тому, що було передано. Якщо він не збігається, ми встановлюємо для їх refresh_token
    значення None і викликати HTTPException із кодом статусу 401 (Неавторизовано). Якщо він збігається, ми створюємо
    новий маркер доступу (access_token). Ми також генеруємо новий маркер оновлення (refresh_token). Потім ми оновлюєм
    нашу базу даних для зберігання нового (refresh_token).

    Args:
    email: str: Email користувача
    token: str: Токен взятий з request
    session: Session: Передача сеанса бази даних у функцію

    Returns:
    access_token та refresh_token
    """
    user = await get_user_by_email(email, session)
    if user.refresh_token != token:
        await reset_refresh_token(user=user, session=session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"email": user.email})                                        # noqa
    refresh_token = await create_refresh_token(data={"email": user.email})  # noqa
    user.refresh_token = refresh_token
    session.commit()
    return access_token, refresh_token
