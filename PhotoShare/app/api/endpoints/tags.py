from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from PhotoShare.app.core.database import get_db
from PhotoShare.app.repositories import tags as repository_tags
from PhotoShare.app.schemas.photo import TagModel, TagResponse

router = APIRouter(prefix='/tags', tags=["tags"])


@router.get("/", response_model=List[TagResponse])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    """
    The read_tags function returns a list of tags.

    :param skip: int: Skip the first n tags
    :param limit: int: Specify the number of tags to return
    :param db: Session: Get a database session, which is used to query the database
    :return: A list of tags
    :doc-author: Trelent
    """
    tags = repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The read_tag function will return a single tag from the database.
    It takes an integer as its argument, which is the ID of the tag to be returned.
    If no such tag exists in the database, it raises a 404 error.

    :param tag_id: int: Specify the type of parameter that is expected
    :param db: Session: Pass the database session from the dependency to the function
    :return: A tag object, which is defined in schemas
    :doc-author: Trelent
    """
    tag = repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse)
def create_tag(body: TagModel, db: Session = Depends(get_db)):
    """
    The create_tag function creates a new tag in the database.

    :param body: TagModel: Pass the request body to the function
    :param db: Session: Pass the database session to the function
    :return: A tagmodel object
    :doc-author: Trelent
    """
    return repository_tags.create_tag(body, db)


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(body: TagModel, tag_id: int, db: Session = Depends(get_db)):
    """
    The update_tag function updates a tag in the database.

    :param body: TagModel: Get the new tag name from the request body
    :param tag_id: int: Identify the tag to be deleted
    :param db: Session: Pass the database session to the function
    :return: The updated tag
    :doc-author: Trelent
    """
    tag = repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", response_model=TagResponse)
def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    The remove_tag function removes a tag from the database.
        It takes in an integer representing the id of the tag to be removed, and returns a dictionary containing
        information about that tag.

    :param tag_id: int: Specify the tag id of the tag to be deleted
    :param db: Session: Pass the database session to the repository function
    :return: The tag that was removed
    :doc-author: Trelent
    """
    tag = repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
