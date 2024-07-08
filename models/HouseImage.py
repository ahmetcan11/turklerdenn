from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from db.base_class import Base
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .house import House


class HouseImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("house.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    house = relationship("House", back_populates="images")
