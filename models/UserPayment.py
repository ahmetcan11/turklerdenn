from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, Float
from db.base_class import Base


class UserPayment(Base):
    payment_id = Column(String, primary_key=True, index=True)
    email = Column(String)
