from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func, Table
from sqlalchemy.orm import relationship

from db.base_class import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class General(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime, default=func.now())
    address = Column(String, nullable=True)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    post_id = Column(String, unique=True)
    description = Column(String)
    total_comments_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    upvote = Column(Integer, default=0)
    downvote = Column(Integer, default=0)
    interest_id = Column(Integer, ForeignKey('interest.id'))
    interest = relationship("Interest", back_populates="posts")    # Change the comments field to a one-to-many relationship
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="generals")  # Use plural "houses"
    images = relationship("GeneralImage", back_populates="general")
    latitude = Column(String)
    longitude = Column(String)


class Interest(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Name of the interest
    # Relationship back to General through the association table
    posts = relationship("General", back_populates="interest")


class Comment(Base):
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner_name = Column(String)
    owner_last_name = Column(String)
    created_on = Column(DateTime, default=func.now())
    id = Column(Integer, primary_key=True, index=True)
    upvote = Column(Integer, default=0)
    downvote = Column(Integer, default=0)
    text = Column(String)
    post_id = Column(Integer, ForeignKey('general.id'))
    # Define a relationship back to the General model
    post = relationship("General", back_populates="comments")
    # Add a new relationship for nested comments
    parent_comment_id = Column(Integer, ForeignKey('comment.id'))
    nested_comments = relationship("Comment", back_populates="parent_comment", remote_side=[id])
    parent_comment = relationship("Comment", back_populates="nested_comments", remote_side=[parent_comment_id])


class GeneralImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    general_id = Column(Integer, ForeignKey("general.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    general = relationship("General", back_populates="images")
