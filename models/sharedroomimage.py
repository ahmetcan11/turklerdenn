from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base_class import Base


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .sharedroom import SharedRoom  # noqa: F401


class SharedRoomImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    shared_room_id = Column(Integer, ForeignKey("sharedroom.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    sharedroom = relationship("SharedRoom", back_populates="images")
