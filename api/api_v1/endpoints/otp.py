import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.Otp import otp_schema
from crud import crud_otp
from api import deps
from utils import emailUtil, otpUtil

router = APIRouter()


@router.post("/send")
def send_otp(
    *,
    db: Session = Depends(deps.get_db),
    otp_in: otp_schema.OtpCreate,
):
    # Check block OTP
    opt_blocks = crud_otp.otpBlocks.find_otp_block(db)
    print("OPT BLOCKS : ", opt_blocks)
    if opt_blocks:
        raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked in 5 minutes")

    # Generate and save to table OTPs
    otp_code = otpUtil.random(6)
    session_id = str(uuid.uuid1())
    crud_otp.otp.save_otp(db=db, otp_in=otp_in, session_id=session_id, otp_code=otp_code)
    emailUtil.send_email2(otp_code, otp_in)
    return {
        "session_id": session_id
    }


@router.post("/verify")
def verify_otp(
    *,
    db: Session = Depends(deps.get_db),
    otp_in: otp_schema.OtpVerify,
):
    # Check block OTP
    opt_blocks = crud_otp.otpBlocks.find_otp_block(db)
    print("OPT BLOCKS : ", opt_blocks)
    if opt_blocks:
        raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked in 5 minutes")

    # Check OTP code 6 digit lifetime
    otp_result = crud_otp.otp.find_otp_life_time(db=db, recipient_id=otp_in.recipient_id, session_id=otp_in.session_id)
    if not otp_result:
        raise HTTPException(status_code=404, detail="OTP code has expired, please request a new one.")

    otp_result = otp_schema.OtpInfo(**otp_result)

    # Check if OTP code is already used
    if otp_result.status == "9":
        raise HTTPException(status_code=404, detail="OTP code has used, please request a new one.")

    # Verify OTP code, if not verified,
    if otp_result.otp_code != otp_in.otp_code:
        # Increment OTP failed count
        # await crud_otp.otp.save_otp_failed_count(otp_result)

        # If OTP failed count = 5
        # then block otp
        if otp_result.otp_failed_count + 1 == 5:
            # await crud.save_block_otp(otp_result)
            raise HTTPException(status_code=404, detail="Sorry, this phone number is blocked in 5 minutes")

        # Throw exceptions
        raise HTTPException(status_code=404, detail="The OTP code you've entered is incorrect.")

    # Disable otp code when succeed verified
    # await crud_otp.disable_otp(otp_result)

    return {
        "status_code": 200,
        "detail": "OTP verified successfully"
    }
