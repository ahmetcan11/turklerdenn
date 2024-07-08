import base64
import hashlib
import uuid
from datetime import timedelta
from typing import Any, Optional, List
import requests
from cryptography.fernet import Fernet
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError
from schemas.Business import business_schema
from schemas.User import user_schema
from crud import crud_user, crud_business, crud_business_image
from core import security
from core.config import settings
from schemas.Otp import otp_schema
from crud import crud_otp
from api import deps
from utils import emailUtil, otpUtil
from utils.googleBucket import upload_business_profile_image
from sqlalchemy.orm import Session
from utils.common_util import validate_phone_number
import sqlalchemy

router = APIRouter()


# dummy
@router.get("/health")
def get_message():
    return {"message": "Hello from turklerden.com"}


@router.post("/login")
def login_access_token(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud_user.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user_id": user.id
    }


@router.post("/alternate_login")
def login_access_token(
        db: Session = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud_user.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        return None
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user_id": user.id
    }


@router.post("/register")
def register_user(
        *,
        db: Session = Depends(deps.get_db),
        email: str = Body(...),
        password: str = Body(...),
        first_name: str = Body(None),
        last_name: str = Body(None),
        tel_number: str = Body(None),
        whatsapp_number: str = Body(None)
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if tel_number and len(tel_number) <= 4:  # Assuming country codes are 3 digits max
        tel_number = None
    if whatsapp_number and len(whatsapp_number) <= 4:  # Assuming country codes are 3 digits max
        whatsapp_number = None
    # Validate phone numbers
    if tel_number:
        validate_phone_number(tel_number)
    if whatsapp_number:
        validate_phone_number(whatsapp_number)
    existing_user = crud_user.user.get_by_email(db, email=email)
    if existing_user:
        if existing_user.is_active:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system and is active",
            )
        else:
            # User with the same email exists but is inactive, update the password
            new_user = crud_user.user.reset_password(db, password=password, email=email)
    else:
        # No user with the same email exists, create a new user
        user_in = user_schema.UserCreate(
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tel_number=tel_number,
            whatsapp_number=whatsapp_number,
            is_active=False  # You can set this to True if you want the new user to be active immediately
        )
        new_user = crud_user.user.create(db, obj_in=user_in)

    encrypted_password = encrypt_password(password, first_name, last_name, email)
    otp_in_data = {
        "recipient_id": email,
        "encrypted_password": encrypted_password,
        "first_name": first_name,
        "last_name": last_name
    }
    otp_in = otp_schema.OtpCreate(**otp_in_data)
    session_id = send_first_otp(otp_in, db)

    # chat_engine method will register a new user to the chat engine platform

     #chat_engine(first_name, last_name, email, password)
    return {
        "user_id": new_user.id,
        "session_id": session_id["session_id"],
        "email": session_id["email"]
    }


def chat_engine(first_name: str, last_name: str, email: str, password: str):
    user_name = first_name + last_name

    # Define the API endpoint and headers
    url = 'https://api.chatengine.io/users/'
    headers = {
        'PRIVATE-KEY': 'dca5b651-9ce3-4d3e-adbd-07a340b9aa4f'  # Replace with your actual private key
    }

    # Define the payload
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "username": user_name,  # Required
        "secret": password,  # Required
        "email": email  # Email
    }

    # Local image path

    # Make sure tha this path works correctly
    # image_urls
    # /Users/emreyanmis/Desktop/123.png

    # TODO: image selection will be implemented later on
    # image_path = image_urls # Replace with the path to your local image
    #
    # # Open the image file in binary mode
    # with open(image_path, 'rb') as image_file:
    #     files = {
    #         'avatar': image_file
    #     }
    #     # Make the POST request to create the user
    response = requests.post(url, headers=headers, data=data)

    # Print the response
    # TODO: Put those logs in the cloud logs
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')

    return response


@router.post("/businessRegister", response_model_exclude={"hashed_password", "is_superuser", "created_on"})
def business_registration(
        email: str = Form(...),
        first_name: str = Form(None),
        last_name: str = Form(None),
        password: str = Form(...),
        name: str = Form(...),
        is_online: bool = Form(None),
        address: str = Form(...),
        country: str = Form(...),
        state: str = Form(...),
        city: str = Form(...),
        category_list: str = Form(...),
        description: str = Form(None),
        website: str = Form(None),
        tel_number: str = Form(None),
        whatsapp_number: str = Form(None),
        images: Optional[List[UploadFile]] = File(None),
        db: Session = Depends(deps.get_db),
) -> Any:
    if tel_number and len(tel_number) <= 4:  # Assuming country codes are 3 digits max
        tel_number = None
    if whatsapp_number and len(whatsapp_number) <= 4:  # Assuming country codes are 3 digits max
        whatsapp_number = None
    # Validate phone numbers
    if tel_number:
        validate_phone_number(tel_number)
    if whatsapp_number:
        validate_phone_number(whatsapp_number)
    existing_user = crud_user.user.get_by_email(db, email=email)
    if existing_user:
        if existing_user.is_active:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system and is active",
            )
        else:
            business_id = crud_business.business.get_by_owner_id(db, owner_id=existing_user.id).id
            crud_business_image.delete_all(db, business_id=business_id)
            crud_business.business.delete_by_owner_id(db, owner_id=existing_user.id)
            crud_user.user.delete(db, email=email)

    try:
        # Create the user and business and Upload the file to Google Cloud Storage
        if images:
            image_urls = upload_business_profile_image(str(name), images)
            new_user = crud_user.user.create_with_business(db, obj_in=business_schema.BusinessCreateNoUser(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                name=name,
                is_online=is_online,
                address=address,
                country=country,
                state=state,
                city=city,
                category_list=category_list,
                description=description,
                website=website,
                tel_number=tel_number,
                whatsapp_number=whatsapp_number,
            ), image_urls=image_urls)
        else:
            new_user = crud_user.user.create_with_business(db, obj_in=business_schema.BusinessCreateNoUser(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                name=name,
                is_online=is_online,
                address=address,
                country=country,
                state=state,
                city=city,
                category_list=category_list,
                description=description,
                website=website,
                tel_number=tel_number,
                whatsapp_number=whatsapp_number,
            ), image_urls=["empty"])
        otp_in_data = {
            "recipient_id": email,
        }
        otp_in = otp_schema.OtpCreate(**otp_in_data)
        session_id = send_first_otp(otp_in, db)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        chat_engine(first_name, last_name, email, password)
        return {
            "access_token": security.create_access_token(
                new_user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "user_id": new_user.id,
            "business_id": new_user.businesses[0].id,
            "session_id": session_id["session_id"],
            "email": session_id["email"]
        }
    except sqlalchemy.exc.IntegrityError as e:
        db.rollback()  # Rollback the transaction in case of a database error
        if "unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Unique Constraint, unique key already exists!")
        else:
            raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        # Handle other exceptions (e.g., image upload error)
        if hasattr(e, "detail"):
            detail = e.detail
        else:
            detail = "An error occurred." + str(e)
        raise HTTPException(status_code=500, detail=detail)


@router.post("/send")
def send_otp(
        otp_send: otp_schema.OtpSend,
        db: Session = Depends(deps.get_db),
):
    try:
        # Validate the email using email-validator
        valid = validate_email(otp_send.recipient_id)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address",
        )
    # Check block OTP
    opt_blocks = crud_otp.find_block_otp(db, otp_send.recipient_id)
    otp_result = crud_otp.otp.find_first_otp(db=db, recipient_id=otp_send.recipient_id)
    otp_result = otp_schema.OtpCreate(**otp_result)
    print("OPT BLOCKS : ", opt_blocks)
    if opt_blocks:
        raise HTTPException(status_code=403, detail="Sorry, this email is blocked in 5 minutes")

    # Generate and save to table OTPs
    otp_code = otpUtil.random(6)
    session_id = str(uuid.uuid1())
    crud_otp.otp.save_otp(db=db, otp_in=otp_result, session_id=session_id, otp_code=otp_code)
    emailUtil.send_email2(otp_code, otp_send)
    return {
        "session_id": session_id,
        "email": otp_send.recipient_id
    }


def send_first_otp(
        otp_in: otp_schema.OtpCreate,
        db: Session = Depends(deps.get_db),
):
    try:
        # Validate the email using email-validator
        valid = validate_email(otp_in.recipient_id)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid email address",
        )
    # Check block OTP
    opt_blocks = crud_otp.find_block_otp(db, otp_in.recipient_id)
    if opt_blocks:
        raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked in 5 minutes")

    # Generate and save to table OTPs
    otp_code = otpUtil.random(6)
    session_id = str(uuid.uuid1())
    crud_otp.otp.save_otp(db=db, otp_in=otp_in, session_id=session_id, otp_code=otp_code)
    emailUtil.send_email2(otp_code, otp_in)
    return {
        "session_id": session_id,
        "email": otp_in.recipient_id
    }


def generate_key(first_name: str, last_name: str, email: str) -> bytes:
    # Create a hash of the user's details to generate a key
    key_material = f"{first_name}{last_name}{email}".encode()
    key_hash = hashlib.sha256(key_material).digest()
    key = base64.urlsafe_b64encode(key_hash[:32])  # Fernet keys must be 32 url-safe base64-encoded bytes
    return key


def encrypt_password(password: str, first_name: str, last_name: str, email: str) -> str:
    key = generate_key(first_name, last_name, email)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode())
    return encrypted_password.decode()


def decrypt_password(encrypted_password: str, first_name: str, last_name: str, email: str) -> str:
    key = generate_key(first_name, last_name, email)
    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password.encode())
    return decrypted_password.decode()


@router.post("/verify")
def verify_otp(
        *,
        db: Session = Depends(deps.get_db),
        otp_in: otp_schema.OtpVerify,
):
    opt_blocks = crud_otp.find_block_otp(db, otp_in.recipient_id)
    if opt_blocks:
        raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked for 5 minutes")
    # Check OTP code 6 digit lifetime
    otp_result = crud_otp.otp.find_otp_life_time(db=db, recipient_id=otp_in.recipient_id, session_id=otp_in.session_id)
    if not otp_result:
        raise HTTPException(status_code=404, detail="OTP code has expired, please request a new one.")

    otp_info = otp_schema.OtpInfo(**otp_result)

    # Check if OTP code is already used
    if otp_info.status == "9":
        raise HTTPException(status_code=404, detail="OTP code has used, please request a new one.")

    # Verify OTP code, if not verified,
    if otp_info.otp_code != otp_in.otp_code:
        # Increment OTP failed count
        crud_otp.otp.save_otp_failed_count(db=db,
                                           recipient_id=otp_in.recipient_id,
                                           session_id=otp_in.session_id)
        # If OTP failed count = 5
        # then block otp
        if otp_info.otp_failed_count + 1 >= 5:
            crud_otp.otpBlocks.save_block_otp(db, otp_in.recipient_id)
            raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked for 5 minutes")

        # Throw exceptions
        raise HTTPException(status_code=404, detail="The OTP code you've entered is incorrect.")

    # Disable otp code when succeed verified
    # await crud_otp.disable_otp(otp_result)
    session_data = crud_user.user.verify_user_email(db, email=otp_in.recipient_id)
    otp_result = otp_schema.OtpCreate(**otp_result)

    if session_data.is_active:
        encrypted_password = otp_result.encrypted_password
        decrypted_password = decrypt_password(encrypted_password, otp_result.first_name, otp_result.last_name,
                                              otp_result.recipient_id)
        chat_engine(otp_result.first_name, otp_result.last_name, otp_result.recipient_id, decrypted_password)
        

    return otp_result