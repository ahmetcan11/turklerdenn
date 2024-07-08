from typing import Optional

from pydantic import BaseModel, EmailStr
from schemas.Business import business_schema
from schemas.Free import free_schema
from schemas.Event import event


class OurBaseModel(BaseModel):
    class Config:
        orm_mode = True


# Shared Properties
class UserBase(OurBaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True
    tel_number: Optional[str] = None
    whatsapp_number: Optional[str] = None

class UserPublic(OurBaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id: Optional[int]  # Make the id field optional
    businesses: business_schema.BusinessCreateNoUser
    free_items: free_schema.FreeCreate
    events: event.EventCreate


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: Optional[int] = None


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    password: str


class UserCreateWithBusiness(UserBase):
    email: str
    password: str
    businesses: business_schema.BusinessCreateNoUser


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    # stripe_customer_id: Optional[str] = None


# Additional properties to return via API
class User(UserInDBBase):
    pass
