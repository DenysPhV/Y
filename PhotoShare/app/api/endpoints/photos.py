from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File, Response
from sqlalchemy.orm import Session

from PhotoShare.app.core.config import settings
from PhotoShare.app.core.database import get_db
from PhotoShare.app.models.user import User
from PhotoShare.app.repositories import photo as photo_repository
from PhotoShare.app.schemas.photo import PhotoResponse, PhotoModel, PhotoUpdate
from PhotoShare.app.services.auth_service import get_current_user
from PhotoShare.app.services.photo_service import CloudinaryService

router = APIRouter(prefix='/photos', tags=["photos"])


@router.get("/", response_model=List[PhotoResponse])
def get_photos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=200),
               db: Session = Depends(get_db)):

    """
    The get_photos function returns a list of photos.

    :param limit: int: Limit the number of photos returned
    :param ge: Specify the minimum value of the parameter
    :param le: Limit the number of photos returned to 500
    :param offset: int: Specify the number of photos to skip
    :param ge: Specify a minimum value for the limit and offset parameters
    :param le: Limit the number of photos returned
    :param db: Session: Get the database session
    :return: A list of photos
    :doc-author: Trelent
    """
    photos = photo_repository.get_photos(limit, offset, db)
    return photos


@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    The get_photo function is used to retrieve a photo from the database.
        The function takes in a photo_url and returns the corresponding Photo object.

    :param photo_id: str: Get the photo from the database
    :param db: Session: Access the database
    :param user: User: Get the current user
    :return: A photo object
    :doc-author: Trelent
    """
    photo = photo_repository.get_photo(photo_id, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return photo


@router.get("/qr_code/{photo_id}", responses={200: {"content": {"image/png": {}}}}, response_class=Response)
def get_qrcode(photo_id: int, db: Session = Depends(get_db)):

    """
    The get_qrcode function returns the QR code for a given photo.

    :param photo_id: int: Specify the photo id of the image to be retrieved
    :param db: Session: Pass the database session to the function
    :return: The qr code for a given photo id
    :doc-author: Trelent
    """
    code = photo_repository.get_qrcode(photo_id, db)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_FOUND",
        )
    return Response(content=code, media_type="image/png")


@router.post("/", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
def create_photo(body: PhotoModel, file: UploadFile = File(), db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    """
    The create_photo function creates a new photo in the database.
        It takes in a PhotoModel object, an UploadFile object, and a Session object.
        The UploadFile is used to upload the image file to Cloudinary and get its URL.
        The Session is used to create the photo in our database using SQLAlchemy's ORM.

    :param body: PhotoModel: Create a new photo object
    :param file: UploadFile: Upload the photo to cloudinary
    :param db: Session: Get the database session
    :param user: User: Get the user who is currently logged in
    :return: A photo object
    :doc-author: Trelent
    """
    public_id = CloudinaryService.get_public_id(filename=file.filename)
    photo_load = CloudinaryService.upload_photo(file=file.file, public_id=public_id)
    photo_edit = CloudinaryService.edit_photo(photo=photo_load)
    version = photo_edit.get('version')
    photo_url = CloudinaryService.get_photo(public_id=public_id, version=version)
    photo = photo_repository.create_photo(body, photo_url, db, user)
    return photo


@router.put("/{photo_id}", response_model=PhotoResponse)
def update_contact(body: PhotoUpdate, photo_id: int = Path(ge=1), db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    """
    The update_contact function updates a contact in the database.
        Args:
            body (PhotoUpdate): The updated contact information.
            photo_id (int): The id of the contact to update.

    :param body: PhotoUpdate: Pass the new values for the photo to be updated
    :param photo_id: int: Specify the id of the photo to be updated
    :param db: Session: Pass in the database session to the function
    :param user: User: Get the current user
    :return: The updated photo
    :doc-author: Trelent
    """
    photo = photo_repository.update_photo(photo_id, body, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return photo


@router.delete("/{photo_id}", response_model=PhotoResponse)
def delete_contact(photo_id: int = Path(ge=1), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            photo_id (int): The id of the contact to delete.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            user (User, optional): User object containing information about the current user's session. Defaults to
            Depends(get_current_user).

    :param photo_id: int: Specify the photo to be deleted
    :param db: Session: Get a database session
    :param user: User: Get the current user
    :return: The deleted contact
    :doc-author: Trelent
    """
    photo = photo_repository.remove_photo(photo_id, db, user)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return photo
