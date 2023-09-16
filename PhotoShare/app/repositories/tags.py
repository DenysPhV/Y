from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from PhotoShare.app.models.photo import Tag
from PhotoShare.app.schemas.photo import TagModel


def get_tags(offset: int, limit: int, db: Session) -> List[Tag]:

    """
    The get_tags function returns a list of tags from the database.
        Args:
            offset (int): The number of items to skip before starting to collect the result set.
            limit (int): The numbers of items to return after offset has been applied.

    :param offset: int: Specify the offset of the first row to return
    :param limit: int: Limit the number of tags returned
    :param db: Session: Pass the database session to the function
    :return: A list of tags
    :doc-author: Trelent
    """
    sq = select(Tag).offset(offset).limit(limit)
    tags = db.execute(sq)
    return tags.scalars().all()


def get_tag(tag_id: int, db: Session):

    """
    The get_tag function returns a single tag from the database.
        Args:
            tag_id (int): The id of the desired tag.
            db (Session): A connection to the database.

    :param tag_id: int: Specify the id of the tag we want to get
    :param db: Session: Pass the database session into the function
    :return: A single row from the tag table
    :doc-author: Trelent
    """
    sq = select(Tag).filter_by(id=tag_id)
    tag = db.execute(sq)
    return tag.scalar_one_or_none()


def create_tag(body: TagModel, db: Session) -> Tag:

    """
    The create_tag function creates a new tag in the database.

    :param body: TagModel: Specify the type of data that will be passed into the function
    :param db: Session: Access the database
    :return: The created tag object
    :doc-author: Trelent
    """
    tag = db.query(Tag).filter_by(name=body.name).first()
    if tag is None:
        tag = Tag(name=body.name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag


def update_tag(tag_id: int, body: TagModel, db: Session) -> Tag | None:

    """
    The update_tag function updates a tag in the database.
        Args:
            tag_id (int): The id of the tag to update.
            body (TagModel): The updated Tag object with new values for name and description.

    :param tag_id: int: Identify the tag to be updated
    :param body: TagModel: Pass in the new tag name
    :param db: Session: Access the database
    :return: The updated tag object
    :doc-author: Trelent
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        tag .name = body.name
        db.commit()
    return tag


def remove_tag(tag_id: int, db: Session) -> Tag | None:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
