from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session

from PhotoShare.app.core.database import get_db
from PhotoShare.app.models.rating import Rating
from PhotoShare.app.models.user import User
from PhotoShare.app.repositories import photo as photo_repository
from PhotoShare.app.repositories import rating as rating_repository
from PhotoShare.app.schemas.rating import RatingResponse, RatingModel
from PhotoShare.app.services.auth_service import get_current_user
from PhotoShare.app.services import roles

router_rating = APIRouter(prefix="/rating", tags=["rating"])


@router_rating.get("/", response_model=List[RatingResponse],
                   dependencies=[Depends(roles.Roles(['admin', 'moderator']))])
def get_ratings(photo_id: int, db: Session=Depends(get_db)):
    photo = photo_repository.get_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    ratings = rating_repository.get_ratings(db, photo_id=photo_id)
    return ratings


@router_rating.get("/{rating_id}", response_model=RatingResponse,
                   dependencies=[Depends(roles.Roles(['admin', 'moderator']))])
def get_rating(rating_id: int, db: Session=Depends(get_db)):
    rating = rating_repository.get_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    return rating


@router_rating.delete("/{rating_id}", response_model=RatingResponse,
                      dependencies=[Depends(roles.Roles(['admin', 'moderator']))])
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    """
    Deletes a rating with specified ID.

    :param rating_id: ID of the rating that is to be deleted.
    :type raiting_id: int
    :param db:
    :type db:
    :return:
    :rtype:
    """
    rating = rating_repository.delete_rating(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    photo_repository.calculate_rating(rating.photo_id, db)
    return rating


@router_rating.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def add_rating(body: RatingModel, photo_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    """
    """
    photo = photo_repository.get_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    if rating_repository.get_ratings(db, photo_id=photo_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="current user have already rated this photo")
    if photo.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="the user can not rate their own photo")
    if body.rating not in range(1, 6):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rating must be between 1 and 5 inclusively")
    rating = rating_repository.add_rating(body, photo_id, current_user.id, db)
    photo_repository.calculate_rating(photo_id, db)
    return rating
