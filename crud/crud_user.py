from typing import Any, Dict, Optional, Union, List, Type

from sqlalchemy.orm import Session, joinedload

from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from models.businessImage import BusinessImage
from models.user import User
from models.business import Business
from schemas.User.user_schema import UserCreate, UserUpdate, UserCreateWithBusiness
from utils.common_util import get_coordinates_for_address


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def delete(self, db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
            return user
        return None

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, *, id: int) -> Optional[User]:
        return db.query(User).filter(User.id == id).options(
            joinedload(User.events),
            joinedload(User.shared_rooms),
            joinedload(User.free_items),
            joinedload(User.businesses)
        ).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            tel_number=obj_in.tel_number,
            whatsapp_number=obj_in.whatsapp_number,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_business(
            self, db: Session, *, obj_in: UserCreateWithBusiness,
            image_urls: List[str]) -> User:
        coordinates = get_coordinates_for_address(
            obj_in.address + " " + obj_in.city + " "
            + obj_in.state + " " + obj_in.country)
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            tel_number=obj_in.tel_number,
            whatsapp_number=obj_in.whatsapp_number,
        )

        # Create a single business object
        business = Business(
            name=obj_in.name,
            address=obj_in.address,
            country=obj_in.country,
            state=obj_in.state,
            city=obj_in.city,
            latitude=coordinates.get('latitude'),
            longitude=coordinates.get('longitude'),
            category_list=obj_in.category_list,
            description=obj_in.description,
            website=obj_in.website,
            tel_number=obj_in.tel_number,
            whatsapp_number=obj_in.whatsapp_number,
            is_online=obj_in.is_online
        )

        # Create BusinessImage objects for each image URL and associate them with the business
        for image_url in image_urls:
            business_image = BusinessImage(image_url=image_url)
            business.images.append(business_image)

        # Associate the business with the user and save to the database
        db_obj.businesses.append(business)
        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        first_business = db_obj.businesses[0]
        first_business.post_id = "business-" + str(first_business.id)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def reset_password(self, db: Session, *, password: str, email: str) -> Optional[User]:
        db_user = db.query(User).filter(User.email == email).first()
        db_user.hashed_password = get_password_hash(password)
        db.commit()
        db.refresh(db_user)
        return db_user

    def verify_user_email(self, db: Session, *, email: str) -> Optional[User]:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            db_user.is_active = True
            db.commit()
            db.refresh(db_user)
        return db_user

    # def update(
    #     self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    # ) -> User:
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     if update_data["password"]:
    #         hashed_password = get_password_hash(update_data["password"])
    #         del update_data["password"]
    #         update_data["hashed_password"] = hashed_password
    #     return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user_check = self.get_by_email(db, email=email)
        if not user_check:
            return None
        if not verify_password(password, user_check.hashed_password):
            return None
        return user_check

    def is_active(self, user_check: User) -> bool:
        return user_check.is_active

    def is_superuser(self, user_check: User) -> bool:
        return user_check.is_superuser


user = CRUDUser(User)
