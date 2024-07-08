from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base_class import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .sharedroomimage import SharedRoomImage


class SharedRoom(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    title = Column(String, index=True)
    price = Column(String)
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    description = Column(String)
    created_on = Column(DateTime, default=func.now())
    furniture_available = Column(Boolean, default=False)
    images = relationship("SharedRoomImage", back_populates="sharedroom")
    views = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="shared_rooms")  # Use plural "businesses"
    latitude = Column(String)
    longitude = Column(String)
