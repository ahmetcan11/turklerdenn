from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from db.base_class import Base
from sqlalchemy.orm import relationship

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .job import Job


class JobImage(Base):
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job.id"))
    image_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=func.now())
    job = relationship("Job", back_populates="images")
