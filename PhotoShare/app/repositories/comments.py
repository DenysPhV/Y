from typing import List

from datetime import datetime

from sqlalchemy.orm import Session
# from sqlalchemy.sql import extract
# import sqlalchemy as sa


from PhotoShare.app.models.comment import Comment
from PhotoShare.app.models.user import User

from PhotoShare.app.schemas.comment import CommentModel


def get_comments(limit: int, photo_id: int, db: Session) -> List[Comment]:
    """
    Retrieves a list of comments on a specific post.

    :param limit: Maximum number of comments to return.
    :type limit: int
    :param photo_id: ID of the post.
    :type photo_id: int
    :param db: The database session.
    :type db: Session
    :return: A list of comments.
    :rtype: List[Comment]
    """
    return db.query(Comment).filter(Comment.photo_id==photo_id).limit(limit).all()


def get_comment(comment_id: int, db: Session) -> Comment:
    """
    Retrieves a comment with a specific ID.

    :param comment_id: The ID of the comment.
    :type comment_id: int 
    :param db: The database session.
    :type db: Session
    :return: The comment.
    :rtype: Comment
    """
    return db.query(Comment).filter(Comment.id==comment_id).first()

def create_comment(body: CommentModel, user: User, photo_id: int, db: Session) -> Comment:
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
    :return: The newly added comment.
    :rtype: Comment
    """
    comment = Comment(content=body.content, user_id=user.id, photo_id=photo_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def update_comment(body: CommentModel, comment_id: int, db: Session) -> Comment:
    """
    Updates the comment

    :param body: The data to use when updating the comment.
    :type body: CommentModel
    :param comment_id: id of a comment to update.
    :type comment_id: int
    :param db: The database session.
    :type db: Session
    :return: The updated comment.
    :rtype: Comment
    """
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        comment.content = body.content
        db.commit()
    return comment

def delete_comment(comment_id: int, db: Session) -> Comment:
    """
    Deletes the comment
    
    :param comment_id: id of a comment to delete.
    :type comment_id: int
    :param db: The database session.
    :type db: Session
    :return: The deleted comment.
    :rtype: Comment
    """
    comment = db.query(Comment).filter(Comment.id==comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment