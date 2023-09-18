from typing import List

from sqlalchemy.orm import Session

from PhotoShare.app.models.rating import Rating
from PhotoShare.app.schemas.rating import RatingModel


def get_ratings(db: Session, photo_id: int = 0, user_id: int = 0) -> List[Rating]:
    """
    Returns list of ratings.

    :param db: The database session.
    :type db: Session
    :param photo_id: Id of the photo which rating to find. If 0 finds ratings on all photos.
    :type photo_id: int
    :param user_id: Id of the user whose rating to find. If 0 finds ratings by all users.
    :type user_id: int
    :return: The list of ratings.
    :rtype: List[int]
    """
    if photo_id and user_id:
        ratings = db.query(Rating).filter(Rating.photo_id == photo_id, Rating.user_id == user_id).all()
    elif photo_id and not user_id:
        ratings = db.query(Rating).filter(Rating.photo_id == photo_id).all()
    elif user_id and not photo_id:
        ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    else:
        ratings = db.query(Rating).all()

    return ratings


def get_rating(rating_id: int, db: Session) -> Rating:
    """
    Returns a rating with the specified ID.

    :param rating_id: The ID of the rating to be found.
    :type rating_id: int
    :param db: The database session.
    :type db: Session
    :return: The found rating.
    :rtype: Rating
    """
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    return rating


def add_rating(body: RatingModel, photo_id: int, user_id: int, db: Session) -> Rating:
    """
    Posts a new rating rating.

    :param body: Data for creating a rating.
    :type body: RatingModel
    :param photo_id: The ID of the photo on wich the rating is posted.
    :type photo_id: int
    :param user_id: The ID of the user that posts a rating.
    :type user_id: int
    :param db: The database session.
    :type db: Session
    :return: New rating.
    :rtype: Rating
    """
    rating = Rating(rating=body.rating, user_id=user_id, photo_id=photo_id)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating


def delete_rating(rating_id: int, db: Session) -> Rating:
    """
    Deletes a specified rating.

    :param rating_id: ID of the rating to be deleted.
    :type rating_id: int
    :param db: The database session.
    :type db: Session
    :return: The deleted rating.
    :rtype: Rating
    """
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if rating:
        db.delete(rating)
        db.commit()
    return rating
