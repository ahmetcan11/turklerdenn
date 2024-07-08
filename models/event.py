from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from db.base_class import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .EventImage import EventImage


class Event(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    title = Column(String, index=True)
    description = Column(String)
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    start_time = Column(DateTime)
    images = relationship("EventImage", back_populates="event")
    views = Column(Integer, default=0)
    online = Column(Boolean)
    price = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    created_on = Column(DateTime, default=func.now())
    owner = relationship("User", back_populates="events")  # Use plural "businesses"
    latitude = Column(String)
    longitude = Column(String)


