from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func, Float, Numeric
from db.base_class import Base
from sqlalchemy.orm import relationship
from .IDGenerationService import id_service
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .FreeImage import FreeImage


class Free(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    title = Column(String, index=True, nullable=False)
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    description = Column(String)
    views = Column(Integer, default=0)
    images = relationship("FreeImage", back_populates="free_item")
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="free_items")
    created_on = Column(DateTime, default=func.now())

