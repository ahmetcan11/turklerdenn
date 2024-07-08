from typing import Optional
from pydantic import BaseModel


class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    reset_password_token: str
    new_password: str
    confirm_password: str
