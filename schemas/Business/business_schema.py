from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, EmailStr


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


# Shared Properties
class BusinessBase(BaseModel):
    name: str
    address: str
    country: str
    state: str
    city: str
    category_list: str
    description: Optional[str] = None
    website: Optional[str] = None
    tel_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    user_rating_count: Optional[int] = None
    rating: Optional[float] = None
    place_id: Optional[str] = None

    # image_urls: List[str] = []  # Use List[str] to make it a list of strings


# Properties to receive via API on creation
class BusinessCreate(BusinessBase):
    name = str
    is_online: Optional[bool] = False


# Properties to receive via API on creation
class BusinessCreateNoUser(BusinessCreate):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str


# Properties to receive via API on update
class BusinessUpdate(BusinessBase):
    name: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    category_list: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    tel_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    is_online: Optional[bool] = False

class PlaceRequest(BaseModel):
    place_id: str
    description: str

class UpdateRequestStatus(BaseModel):
    place_id: str
    approved_status: str

class BusinessApprove(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"
    IN_REVIEW = "in_review"

# Additional properties to return via API
class Business(BusinessBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True