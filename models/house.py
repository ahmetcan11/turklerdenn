from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base_class import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .HouseImage import HouseImage  # Assuming you have a HouseImage model


class House(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    title = Column(String, index=True)
    price = Column(String)
    square_feet = Column(Integer)  # Added square_feet column
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    description = Column(String)
    house_type = Column(String)
    created_on = Column(DateTime, default=func.now())
    views = Column(Integer, default=0)
    images = relationship("HouseImage", back_populates="house")  # Update to HouseImage
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="houses")  # Use plural "houses"
    latitude = Column(String)
    longitude = Column(String)
