from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base_class import Base


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .event import Event  # noqa: F401


class EventImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("event.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    event = relationship("Event", back_populates="images")
