from typing import Optional

from pydantic import BaseModel


class OtpCreate(BaseModel):
    recipient_id: str
    first_name: str
    last_name: str
    encrypted_password: str

class OtpSend(BaseModel):
    recipient_id: str


class OtpUpdate(BaseModel):
    session_id: str
    otp_code: str


class OtpVerify(BaseModel):
    recipient_id: str
    session_id: str
    otp_code: str


class OtpInfo(OtpUpdate):
    otp_failed_count: Optional[int] = None
    status: Optional[str] = None


class OTPList(OtpVerify):
    otp_failed_count: int
    status: str
