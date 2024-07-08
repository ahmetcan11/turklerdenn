from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from db.base_class import Base
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .business import Business  # noqa: F401


class BusinessImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    business = relationship("Business", back_populates="images")
