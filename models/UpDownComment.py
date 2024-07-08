from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class UpDownComment(Base):
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer)
    user_id = Column(Integer)
    upvote = Column(Boolean, default=False)
    downvote = Column(Boolean, default=False)
