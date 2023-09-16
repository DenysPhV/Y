from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from PhotoShare.app.core.database import get_db
from PhotoShare.app.services import auth_service
from PhotoShare.app.services import roles

from PhotoShare.app.models.user import User

from PhotoShare.app.schemas.comment import CommentModel, CommentResponse

from PhotoShare.app.repositories import comments as repository_comments
from PhotoShare.app.repositories import photo as repository_photos

router_comments = APIRouter(prefix='/comments', tags=["comments"])


@router_comments.get("/", response_model=List[CommentResponse])
def read_comments(limit: int = 100, photo_id: int = 0, db: Session = Depends(get_db)):
    """
    Retrieves a list of comments on a specific post.

    :param limit: Maximum number of comments to return.
    :type limit: int
    :param photo_id: ID of the photo.
    :type photo_id: int
    :param db: The database session.
    :type db: Session
    :return: A list of comments.
    :rtype: List[Comment]
    """
    if not photo_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Photo id is required')
    photo = repository_photos.get_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    comments = repository_comments.get_comments(limit, photo_id, db)
    return comments


@router_comments.get("/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a comment with a specific ID.

    :param comment_id: The ID of the comment.
    :type comment_id: int 
    :param db: The database session.
    :type db: Session
    :return: The comment.
    :rtype: Comment
    """
    comment = repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment



@router_comments.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(body: CommentModel, photo_id: int = 0, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new comment.

    :param body: The data used to create a new comment.
    :type body: CommentModel
    :param photo_id: ID of the photo on which the comment is added.
    :type photo_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: User that adds the comment.
    :type current_user: User
    :return: The newly added comment.
    :rtype: Comment
    """
    if photo_id == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Photo id is required')
    photo = repository_photos.get_photo(photo_id=photo_id, db=db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return repository_comments.create_comment(body, current_user, photo_id, db)


@router_comments.put("/{comment_id}", response_model=CommentResponse)
def update_comment(body: CommentModel, comment_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):

    """
    Updates the comment with specified ID.

    :param body: The data used to create a new comment.
    :type body: CommentModel
    :param db: The database session.
    :type db: Session
    :param current_user: User that updates the comment.
    :type current_user: User
    :return: The newly added comment.
    :rtype: Comment
    """
    comment = repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to edit this comment")
    new_comment = repository_comments.update_comment(body, comment_id, db)
    return new_comment


@router_comments.delete("/{comment_id}", response_model=CommentResponse,
                        dependencies=[Depends(roles.Roles(['admin', 'moderator']))])
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Deletes the comment with specified ID.

    :param body: The data used to create a new comment.
    :type body: CommentModel
    :param db: The database session.
    :type db: Session
    :param current_user: User that deletes the comment.
    :type current_user: User
    :return: The newly added comment.
    :rtype: Comment
    """
    comment = repository_comments.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
