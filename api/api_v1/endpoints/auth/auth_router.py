import uuid
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas.User import user_schema
from . import schema, auth_crud
from crud import crud_user
from core import security
from core.config import settings
from crud import crud_otp
from api import deps
from utils import emailUtil, otpUtil

router = APIRouter()


@router.post("/forgot-password")
async def forgot_password(
        *,
        db: Session = Depends(deps.get_db),
        request: schema.ForgotPassword
):
    result = crud_user.user.get_by_email(db, email=request.email)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    elif not result.is_active:
        raise HTTPException(
            status_code=400,
            detail="User found but it is not active.",
        )
    # Create reset code and save in database
    reset_code = str(uuid.uuid1())
    auth_crud.create_reset_code(db, request.email, reset_code)

    # sending email
    subject = "Turklerden.com Password Reset"
    recipient = request.email
    message ="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Password Reset</title>
    </head>
    <body>
        <p>Hello,</p>
        <p>You have requested to reset your password. Click the link below to reset your password:</p>
        <a href="https://www.turklerden.com/new-password?reset_password_token={1:}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>If you did not request this reset, please ignore this email.</p>
    </body>
    </html>
    """.format(request.email, reset_code)
    emailUtil.reset_email(subject, recipient, message)
    return {"reset_code": reset_code,
            "code": 200,
            "message": "We have sent an email with instructions to reset your password"
            }


@router.post("/reset-password")
async def reset_password(
        *,
        db: Session = Depends(deps.get_db),
        request: schema.ResetPassword
):
    # Check valid reset password token
    reset_token = auth_crud.check_reset_password_token(db, request.reset_password_token)
    if not reset_token:
        raise HTTPException(
            status_code=404,
            detail="Reset password expired, please request a new one.",
        )
    # Check both new and confirm password are matched
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=404,
            detail="New password is not match.",
        )


    new_user = crud_user.user.reset_password(db, password=request.new_password, email=reset_token.email)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    auth_crud.disable_reset_code(db, request.reset_password_token, reset_token.email)

    return {
        "access_token": security.create_access_token(
            new_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer"
        ,
        "user_id": new_user.id
    }