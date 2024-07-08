from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from db.base_class import Base
from typing import TYPE_CHECKING,List

if TYPE_CHECKING:
    from .business import Business
    from .free import Free
    from .event import Event
    from .sharedroom import SharedRoom
    from .house import House
    from .general import General


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    tel_number = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=False)
    is_superuser = Column(Boolean(), default=False)
    businesses = relationship("Business", back_populates="owner")  # Use plural "businesses"
    created_on = Column(DateTime, default=func.now())
    free_items = relationship("Free", back_populates="owner")  # Use plural "businesses"
    events = relationship("Event", back_populates="owner")
    shared_rooms = relationship("SharedRoom", back_populates="owner")
    houses = relationship("House", back_populates="owner")
    jobs = relationship("Job", back_populates="owner")
    generals = relationship("General", back_populates="owner")
    # stripe_customer_id = Column(String, nullable=True)

