from datetime import date

from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from PhotoShare.app.core.database import engine
from PhotoShare.app.models.base import Base
from PhotoShare.app.models.user import User


photo_m2m_tag = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photo.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)



class Photo(Base):
    __tablename__ = "photo"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(String(300), index=True)
    photo_url: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)
    tags: Mapped["Tag"] = relationship("Tag", secondary=photo_m2m_tag, backref="photo")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship('User', backref="photo", lazy='joined')

    rating: Mapped[float] = mapped_column(nullable=True)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)


Base.metadata.create_all(bind=engine)
