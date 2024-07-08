from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from db.base_class import Base
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .free import Free


class FreeImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    free_item_id = Column(Integer, ForeignKey("free.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())

    free_item = relationship("Free", back_populates="images")
