from datetime import date

from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from PhotoShare.app.core.database import engine
from PhotoShare.app.models.base import Base
from PhotoShare.app.models.user import User
from PhotoShare.app.models.photo import Photo

class Rating(Base):
    __tablename__ = "ratings"
    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship('User', backref="rating", lazy='joined', passive_deletes=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photo.id"), nullable=True)
    photo: Mapped["Photo"] = relationship('Photo', backref="ratings", lazy='joined', passive_deletes=True)

Base.metadata.create_all(bind=engine)