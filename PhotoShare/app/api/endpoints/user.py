from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from PhotoShare.app.models.user import User
from PhotoShare.app.services.auth_service import get_current_user
from PhotoShare.app.schemas.user import UserRespond, UserFirstname, UserLastname, UserProfileModel, UserUsername
from PhotoShare.app.core.database import get_db
from PhotoShare.app.repositories.users import update_user, get_user_by_email
from PhotoShare.app.services.photo_service import CloudinaryService

router_user = APIRouter(prefix="/user", tags=["user"])


@router_user.get("/profile/{email}", response_model=UserProfileModel, status_code=status.HTTP_200_OK)
def get_user_profile(email: str, session: Session = Depends(get_db)):
    """
    The get_user_profile function використовується для отримання інформації профілю користувача.
    Ця функція приймає електронний лист і повертає наступне:
    - Адреса електронної пошти користувача, ім’я, прізвище, ім’я користувача та дата створення.
    - Кількість зображень, завантажених користувачем.
    Args:
    email: str: Отримуємо електронну адресу користувача, який увійшов у систему
    session: Session: Передаємо сеанс бази даних у функцію
    Returns:
    Словник інформації про користувача
    """
    user = get_user_by_email(email=email, session=session)
    return user


@router_user.get("/me", response_model=UserRespond, status_code=status.HTTP_200_OK,
                 summary='Отримати інформацію про користувача')
def me(user: User = Depends(get_current_user)):
    """
    Функція me повертає інформацію для активного user
    Args:
    :user: отримюємо активного користувача
    Returns:
    Авторизований користувач
    """
    return user


@router_user.patch("/edit/username/{username}", response_model=UserRespond, status_code=status.HTTP_200_OK)
def change_username(body: UserUsername, user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    """
    Функція змінює username користувача
    Args:
    body.username: str: Отримуємо новий username користувача
    :user: Передаємо користувача в якого буде редактовано username
    :session: Отримуємо сессію для доступа до бази даних
    Returns:
    user: Повертаємо user з оновленими даними
    """
    user.username = body.username
    user = update_user(user, session)
    return user


@router_user.patch("/edit/firstname/{firstname}", response_model=UserRespond, status_code=status.HTTP_200_OK)
def edit_firstname(body: UserFirstname, user: User = Depends(get_current_user),
                         session: Session = Depends(get_db)):
    """
    Функція змінює first_name користувача
    Args:
    body.first_name: str: Отримуємо новий first_name користувача
    :user: Передаємо користувача в якого буде редактовано first_name
    :session: Отримуємо сессію для доступа до бази даних
    Returns:
    user: Повертаємо user з оновленими даними
    """
    user.first_name = body.first_name
    user = update_user(user, session)
    return user


@router_user.patch("/edit/lastname/{lastname}", response_model=UserRespond, status_code=status.HTTP_200_OK)
def edit_lastname(body: UserLastname, user: User = Depends(get_current_user),
                  session: Session = Depends(get_db)):
    """
    Функція змінює last_name користувача
    Args:
    last_name: str: Отримуємо новий last_name користувача
    :user: Передаємо користувача в якого буде редактовано last_name
    :session: Отримуємо сессію для доступа до бази даних
    Returns:
    user: Повертаємо user з оновленими даними
    """
    user.last_name = body.last_name
    user = update_user(user, session)
    return user


@router_user.patch("/edit/avatar", response_model=UserRespond, status_code=status.HTTP_200_OK)
def upload_avatar(file: UploadFile = File(), user: User = Depends(get_current_user),
                  session: Session = Depends(get_db)):
    """
    Функція оновлює avatar користувача, завантажуючи його на сервіс cloudinary
    Args:
    file: str: Отримуємо новий avatar користувача
    :user: Передаємо користувача в якого буде редактовано last_name
    :session: Отримуємо сессію для доступа до бази даних
    Returns:
    user: Повертаємо user з оновленими даними
    """
    public_id = CloudinaryService.get_public_id(filename=file.filename)
    public_id = "Y/avatars/" + public_id
    image = CloudinaryService.upload_photo(file=file.file, public_id=public_id)
    version = image.get('version')
    url = CloudinaryService.get_photo(public_id=public_id, version=version)
    user.avatar = url
    user = update_user(user=user, session=session)
    return user


