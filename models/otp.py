from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from db.base_class import Base


class Otp(Base):
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(String(100))
    session_id = Column(String(100))
    otp_code = Column(String(6))
    status = Column(String(1))
    created_on = Column(DateTime, default=func.now())
    updated_on = Column(DateTime)
    otp_failed_count = Column(Integer, default=0)
    first_name = Column(String(100))
    last_name = Column(String(100))
    encrypted_password = Column(String(100))


class OtpBlocks(Base):
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(String(100))
    created_on = Column(DateTime)


class BlackLists(Base):
    token = Column(String(250), primary_key=True)
    email = Column(String(100))


class Codes(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    reset_code = Column(String(50))
    status = Column(String(1))
    expired_in = Column(DateTime)
