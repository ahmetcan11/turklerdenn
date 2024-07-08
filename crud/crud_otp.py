from typing import Any, Dict, Optional, Union, List

from fastapi.encoders import jsonable_encoder
from pydantic.datetime_parse import datetime
from pydantic.schema import timedelta
from sqlalchemy.orm import Session

from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from schemas.Otp.otp_schema import OtpCreate, OtpUpdate
from models.otp import Otp, OtpBlocks


class CRUDOtp(CRUDBase[Otp, OtpCreate, OtpUpdate]):

    def save_otp_failed_count(self, db: Session, *, recipient_id: str, session_id: str):
        otp_record = db.query(self.model).filter(
            Otp.recipient_id == recipient_id,
            Otp.session_id == session_id
        ).first()
        if otp_record:
            otp_record.otp_failed_count += 1
            db.commit()

    def save_otp(
            self, db: Session, *, otp_in: OtpCreate, session_id, otp_code
    ) -> Otp:
        db_obj = Otp(
            recipient_id=otp_in.recipient_id,
            session_id=session_id,
            first_name=otp_in.first_name,
            last_name=otp_in.last_name,
            encrypted_password= otp_in.encrypted_password,
            otp_code=otp_code
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def find_otp_life_time(
            self, db: Session, *, recipient_id: str, session_id: str
    ):
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        otp_verify = db.query(self.model).filter(Otp.recipient_id == recipient_id,
                                                 Otp.session_id == session_id,
                                                 Otp.created_on >= five_minutes_ago).first()
        if otp_verify:
            # map the attributes of the Otp object to a dictionary
            otp_dict = {
                "id": otp_verify.id,
                "recipient_id": otp_verify.recipient_id,
                "session_id": otp_verify.session_id,
                "otp_code": otp_verify.otp_code,
                "status": otp_verify.status,
                "created_on": otp_verify.created_on,
                "updated_on": otp_verify.updated_on,
                "otp_failed_count": otp_verify.otp_failed_count,
                "first_name": otp_verify.first_name,
                "last_name": otp_verify.last_name,
                "encrypted_password": otp_verify.encrypted_password
            }
            return otp_dict

        return None
    
    def find_first_otp(
            self, db: Session, *, recipient_id: str
    ):
        otp_verify = db.query(self.model).filter(Otp.recipient_id == recipient_id).first()
        if otp_verify:
            # map the attributes of the Otp object to a dictionary
            otp_dict = {
                "id": otp_verify.id,
                "recipient_id": otp_verify.recipient_id,
                "session_id": otp_verify.session_id,
                "otp_code": otp_verify.otp_code,
                "status": otp_verify.status,
                "created_on": otp_verify.created_on,
                "updated_on": otp_verify.updated_on,
                "otp_failed_count": otp_verify.otp_failed_count,
                "first_name": otp_verify.first_name,
                "last_name": otp_verify.last_name,
                "encrypted_password": otp_verify.encrypted_password
            }
            return otp_dict

        return None


otp = CRUDOtp(Otp)


class CRUDOtpBlocks(CRUDBase[OtpBlocks, OtpCreate, OtpUpdate]):

    def find_otp_block(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Any:
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        # otp_block = db.query(self.model).filter(OtpBlocks.create_date >= five_minutes_ago).first()
        otp_block = db.query(OtpBlocks.recipient_id).filter(OtpBlocks.created_on >= five_minutes_ago).first()
        return otp_block

    def save_block_otp(self, db: Session, recipient_id: str):
        current_time = datetime.utcnow()
        otp_block = OtpBlocks(recipient_id=recipient_id, created_on=current_time)
        db.add(otp_block)
        db.commit()
        db.refresh(otp_block)  # Refresh the object to get its new ID
        return otp_block

otpBlocks = CRUDOtpBlocks(OtpBlocks)


def find_block_otp(db: Session, recipient: str):
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

    otp_block = db.query(OtpBlocks).filter(
        OtpBlocks.recipient_id == recipient,
        OtpBlocks.created_on >= five_minutes_ago
    ).first()

    return otp_block


