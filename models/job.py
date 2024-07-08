from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base_class import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .JobImage import JobImage  # Assuming you have a JobImage model


class Job(Base):
    is_active = Column(Boolean(), default=True)
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String, unique=True)
    title = Column(String, index=True)
    description = Column(String)
    address = Column(String)
    country = Column(String)
    state = Column(String)
    city = Column(String)
    business_area = Column(String, nullable=False)
    work_type = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    images = relationship("JobImage", back_populates="job")
    views = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="jobs")
    latitude = Column(String)
    longitude = Column(String)
