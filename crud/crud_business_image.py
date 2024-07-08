from sqlalchemy.orm import Session
from models import businessImage  # Assuming you have imported your model
from typing import Any, Dict, Optional, Union, List, Type
from models.businessImage import BusinessImage

from fastapi.encoders import jsonable_encoder
from sqlalchemy import exc
from sqlalchemy.orm import Session, joinedload

from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from models.business import Business
from schemas.Business.business_schema import BusinessCreate, BusinessUpdate
from models.IDGenerationService import id_service


def get(db: Session, business_image_id: int):
    return db.query(BusinessImage).filter(BusinessImage.id == business_image_id).first()


def delete(db: Session, business_image_id: int):
    db_business_image = get(db, business_image_id)
    if db_business_image:
        db.delete(db_business_image)
        db.commit()
        return db_business_image


def delete_all(db: Session, business_id: int):
    db_business_images = db.query(BusinessImage).filter(BusinessImage.business_id == business_id).all()
    for db_business_image in db_business_images:
        db.delete(db_business_image)
    db.commit()
    return db_business_images


def update_image_url(db: Session, business_id: int, new_image_url: str):
    db_business_image = db.query(BusinessImage).filter(BusinessImage.business_id == business_id).first()

    if db_business_image:
        db_business_image.image_url = new_image_url
        db.commit()
        db.refresh(db_business_image)
        return db_business_image
    return None
