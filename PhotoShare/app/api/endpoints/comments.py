from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from PhotoShare.app.core.database import get_db
from PhotoShare.app.services import auth_service

from PhotoShare.app.models.user import User

from PhotoShare.app.schemas.comment import CommentModel, CommentResponse
from PhotoShare.app.schemas.user import UserModel
from PhotoShare.app.schemas.photo import PhotoModel

from PhotoShare.app.repositories import comments as repository_comments


router = APIRouter(prefix='/comments', tags=["comments"])

@router.get("/", response_model=List[CommentResponse])
async def read_comments(limit: int = 100, post_id: int = 0, db: Session = Depends(get_db)):
    """
    Retrieves a list of comments on a specific post.

    :param limit: Maximum number of comments to return.
    :type limit: int
    :param post_id: ID of the post.
    :type post_id: int
    :param db: The database session.
    :type db: Session
    :return: A list of comments.
    :rtype: List[Comment]
    """
    if not post_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Post id is required')
    comments = await repository_comments.get_comments(limit, post_id, db)
    return comments

@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a comment with a specific ID.

    :param comment_id: The ID of the comment.
    :type comment_id: int 
    :param db: The database session.
    :type db: Session
    :return: The comment.
    :rtype: Comment
    """
    comment = await repository_comments.get_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.post("/", response_model=CommentResponse)
async def create_comment(body: CommentModel, post_id: int = 0, db: Session = Depends(get_db),/
                      current_user: User = Depends(auth_service.get_current_user)):#temp
    """
    Creates a new comment.

    :param body: The data used to create a new comment.
    :type body: CommentModel
    :param user: User that adds the comment. (change when user model is ready)
    :type user: UserModel
    :param post_id: ID of the post on which the comment is added.
    :type post_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: User that adds the comment. (change when user model is ready)
    :type current_user: User
    :return: The newly added comment.
    :rtype: Comment
    """
    if not post_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Post id is required')
    return await repository_comments.create_comment(body, current_user, post_id, db)