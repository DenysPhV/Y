from sqlalchemy import Column, Integer, String, func, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

from PhotoShare.app.models.base import Base


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(ARRAY(DateTime))
    user_id = Column('user_id', ForeignKey('users.id', ondelete='SET NULL'), default=None)
    user = relationship('User', backref='contacts')
    # TODO
    # After the post model is created change next collumns to correspond to it.

    post_id = Column('post_id', ForeignKey('post.id', ondelete='CASCADE'), default=None)
    post = relationship('Post', backref='contacts')

    # When a user is deleted I wish all their comments to remain.
    # But if a post is deleted all it's comments will go down with it.
