from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, func
from sqlalchemy.orm import relationship

from db.base_class import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .businessImage import BusinessImage

class Business(Base):
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    name = Column(String, index=True)
    is_active = Column(Boolean(), default=False)
    is_online = Column(Boolean(), default=True)
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    category_list = Column(String)
    description = Column(String, nullable=True)
    images = relationship("BusinessImage", back_populates="business")
    views = Column(Integer, default=0)
    posts = Column(String, nullable=True)
    events = Column(String, nullable=True)
    website = Column(String, nullable=True)
    tel_number = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True)  # Make owner_id nullable
    owner = relationship("User", back_populates="businesses")  # Use plural "businesses"
    created_on = Column(DateTime, default=func.now())
    latitude = Column(String)
    longitude = Column(String)
    # New fields
    rating = Column(Float, nullable=True)
    user_rating_count = Column(Integer, nullable=True)
    place_id = Column(String, nullable=True)

class BusinessRequest(Base):
    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(String, unique=True, index=True)
    approved_status = Column(String, default="In Review")
    description = Column(String, nullable=True)
