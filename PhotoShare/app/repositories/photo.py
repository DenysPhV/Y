import io
from datetime import datetime

import qrcode
from sqlalchemy import select
from sqlalchemy.orm import Session

from PhotoShare.app.models.photo import Photo, Tag
from PhotoShare.app.models.user import User
from PhotoShare.app.repositories.tags import get_tags
from PhotoShare.app.schemas.photo import PhotoModel, PhotoUpdate

from PhotoShare.app.repositories.rating import get_ratings


def get_photos(limit: int, offset: int, db: Session):
    """
    The get_photos function returns a list of photos from the database.
    Args:
    limit (int): The number of photos to return.
    offset (int): The starting point for the query.  This is used for pagination, so that you can get more than
    one page of results at a time.
    For example, if you have 100 total results and want to get 10 per page, set limit=10 and offset=0 on
    your first request; then set limit=10 and offset=10 on your second request; etc... until you've gotten
    all 100 results back in chunks of 10 each time.&quot;

    :param limit: int: Limit the number of photos returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: Session: Pass the database session to the function
    :return: A list of photos
    :doc-author: Trelent
    """
    sq = select(Photo).offset(offset).limit(limit)
    contacts = db.execute(sq)
    return contacts.scalars().all()


def get_photo(photo_id: int, db: Session):
    """
    The get_photo function takes in a photo_url and returns the corresponding Photo object.
    If no such photo exists, it returns None.

    :param photo_id: str: Specify the id of the photo
    :param db: Session: Create a database session
    :return: A photo object or none if the photo does not exist
    :doc-author: Trelent
    """

    sq = select(Photo).filter_by(id=photo_id)

    contact = db.execute(sq)
    return contact.scalar_one_or_none()


def create_photo(body: PhotoModel, photo_url: str, db: Session, user: User):
    """
    The create_photo function creates a new photo in the database.
    It takes three arguments:
    body (PhotoModel): The PhotoModel object that contains the information for creating a new photo.
    url (str): The URL of the image to be uploaded to Cloudinary and associated with this photo.
    db (Session): A SQLAlchemy Session object used for interacting with our database.

    :param body: PhotoModel: Get the name and description of the photo from the request body
    :param photo_url: str: Store the url of the photo in s3
    :param db: Session: Access the database
    :param user: User: Associate the photo with a user
    :return: The photo object that was created
    :doc-author: Trelent
    """

    photo = Photo(name=body.name, description=body.description, user=user)  # tags=photo_tags,
    photo.photo_url = photo_url
    photo.rating = 0
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def get_qrcode(photo_id: int, db: Session):
    """
    Returns qr code encoding the url of the photo

    :param photo_id: int: ID of the photo.
    :param db: Session: Pass in the database session
    :return: The qr code as a byte array
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        code = qrcode.make(photo.photo_url)
        bytes_code = io.BytesIO()
        code.save(bytes_code, format='PNG')
        return bytes_code.getvalue()
    return photo


def update_photo(photo_id: int, body: PhotoUpdate, db: Session, user: User):
    """
    The update_photo function updates the description of a photo in the database.
    Args:
    photo_id (int): The id of the photo to be updated.
    body (PhotoUpdate): A PhotoUpdate object containing a new description for the specified photo.
    This is passed as JSON data in an HTTP request body, and converted into a PhotoUpdate object by
    FastAPI's Pydantic library.
    See models/photo_update for more information on this class and its attributes.

    :param photo_id: int: Identify the photo to be updated
    :param body: PhotoUpdate: Pass in the new photo description
    :param db: Session: Access the database
    :param user: User: Ensure that the user is authorized to update the photo
    :return: A photo object
    :doc-author: Trelent
    """
    sq = select(Photo).filter_by(id=photo_id, user=user)
    result = db.execute(sq)
    photo = result.scalar_one_or_none()
    if photo is None:
        return None
    photo.description = body.description
    photo.updated_at = photo.updated_at + datetime.now()
    db.commit()
    db.refresh(photo)
    return photo


def remove_photo(photo_id: int, db: Session, user: User):
    """
    The remove_photo function removes a photo from the database.
    Args:
    photo_id (int): The id of the photo to be removed.
    db (Session): A connection to the database.  This is used for querying and deleting photos
    from the database.

    user (User): The user who owns this particular photo, and therefore has permission to delete it.
    
    :param photo_id: int: Identify the photo to be removed
    :param db: Session: Pass in the database session
    :param user: User: Check if the user is authorized to delete a photo
    :return: The photo object that was deleted
    :doc-author: Trelent
    """
    sq = select(Photo).filter_by(id=photo_id, user=user)
    result = db.execute(sq)
    photo = result.scalar_one_or_none()
    if photo:
        db.delete(photo)
        db.commit()
    return photo


def calculate_rating(photo_id: int, db: Session) -> int:
    """
    Calculates rating of a specific photo.

    :param photo_id: The ID of the photo to calculate rating.
    :type photo_id: int
    :param db: Pass in the database
    :type db:
    :return: Calculated rating.
    :rtype: int
    """
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo:
        ratings = get_ratings(db, photo_id=photo_id)
        rating_avg = 0
        if len(ratings):
            n_ratings = [r.rating for r in ratings]
            rating_avg = float(sum(n_ratings)) / len(n_ratings)
        photo.rating = rating_avg
        db.commit()
        db.refresh(photo)
    return rating_avg

