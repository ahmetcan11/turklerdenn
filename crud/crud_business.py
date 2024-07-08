from typing import Any, Dict, Optional, Union, List, Type
from sqlalchemy import cast
from fastapi.encoders import jsonable_encoder
from sqlalchemy import exc, Float
from sqlalchemy.orm import Session, joinedload
from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from models.business import Business, BusinessRequest
from models.businessImage import BusinessImage
from schemas.Business.business_schema import BusinessCreate, BusinessUpdate, UpdateRequestStatus
from models.IDGenerationService import id_service
from utils.common_util import get_coordinates_for_address


class CRUDBusiness(CRUDBase[Business, BusinessCreate, BusinessUpdate]):

    def delete_by_owner_id(self, db: Session, owner_id: int) -> bool:
        try:
            # Find and delete all businesses owned by the specified owner
            db.query(self.model).filter(self.model.owner_id == owner_id).delete()
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    def get_by_id(self, db: Session, *, id: int
                  ) -> Business:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        query = query.filter(self.model.is_active == True)
        return query.options(joinedload(Business.images)).first()

    def activate(self, db: Session, business_id: int) -> Optional[Business]:
        db_obj = self.get(db, id=business_id)
        if db_obj:
            db_obj.is_active = True
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return None

    def create_business_with_owner(
            self, db: Session, *, obj_in: BusinessCreate, owner_id: int, image_urls: List[str]
    ) -> Business:
        obj_in_data = jsonable_encoder(obj_in)
        business_data = {
            'name': obj_in_data.get('name'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            'category_list': obj_in_data.get('category_list'),
            'description': obj_in_data.get('description'),
            'website': obj_in_data.get('website'),
            'tel_number': obj_in_data.get('el_number'),
            'whatsapp_number': obj_in_data.get('whatsapp_number'),
            'owner_id': owner_id,
            'is_online': obj_in_data.get('is_online')
        }
        db_obj = Business(
            **business_data
        )
        for image_url in image_urls:
            business_image = BusinessImage(image_url=image_url)
            db_obj.images.append(business_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "business-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj
    
    def create_business_without_owner(
                self, db: Session, *, obj_in: BusinessCreate, image_urls: List[str]
        ) -> Business:
            obj_in_data = jsonable_encoder(obj_in)
            parts = [obj_in_data.get(field) for field in ['address', 'city', 'state', 'country']]
            full_address = " ".join(filter(None, parts))  # This will only include non-None and non-empty strings

            # Only attempt to get coordinates if the full_address is not empty
            if full_address.strip():
                coordinates = get_coordinates_for_address(full_address)
                latitude = coordinates.get('latitude')
                longitude = coordinates.get('longitude')
            else:
                # If there's no address, or it's insufficient, set latitude and longitude to None or default values
                latitude = None
                longitude = None
            business_data = {
                'name': obj_in_data.get('name'),
                'address': obj_in_data.get('address'),
                'country': obj_in_data.get('country'),
                'state': obj_in_data.get('state'),
                'city': obj_in_data.get('city'),
                "latitude": latitude,
                "longitude": longitude,
                'category_list': obj_in_data.get('category_list'),
                'description': obj_in_data.get('description'),
                'website': obj_in_data.get('website'),
                'tel_number': obj_in_data.get('tel_number'),
                'whatsapp_number': obj_in_data.get('whatsapp_number'),
                'rating': obj_in_data.get('rating'),
                'user_rating_count': obj_in_data.get('user_rating_count'),
                'place_id': obj_in_data.get('place_id'),
                'is_online': obj_in_data.get('is_online')
            }
            db_obj = Business(
                **business_data
            )
            for image_url in image_urls:
                business_image = BusinessImage(image_url=image_url)
                db_obj.images.append(business_image)

            db.add(db_obj)
            db.flush()  # Flush to generate the db_obj.id
            db_obj.post_id = "business-" + str(db_obj.id)
            db.commit()  # Commit everything in one go
            db.refresh(db_obj)
            return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Type[Business]]:
        return (
            db.query(self.model)
            .filter(Business.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_active(self, business_check: Business) -> bool:
        return business_check.is_active

    def search_businesses(self, db: Session, country: str = None, state: str = None, city: str = None,
                          category_list: List[str] = None, is_online: bool = None,
                          bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
                          tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
                          keyword: str = None, sort_by_top_post: bool = False, sort_by_fresh_post: bool = False, skip: int = 0, limit: int = 100) -> List[Type[Business]]:
        sort_style_top_post = self.model.views.desc()
        sort_style_fresh_post = self.model.created_on.desc()
        query = db.query(self.model)

        if bl_latitude is not None and bl_longitude is not None and tr_latitude is not None and tr_longitude is not None:
            query = query.filter(
                cast(self.model.latitude, Float) >= bl_latitude,
                cast(self.model.latitude, Float) <= tr_latitude,
                cast(self.model.longitude, Float) >= bl_longitude,
                cast(self.model.longitude, Float) <= tr_longitude
            )

        if country:
            query = query.filter(self.model.country == country)
        if state:
            query = query.filter(self.model.state == state)
        if city:
            query = query.filter(self.model.city == city)
        if category_list:
            # Filter businesses with categories that match any value in the provided category list
            query = query.filter(self.model.category_list.in_(category_list))
        if is_online is not None:
            query = query.filter(self.model.is_online == is_online)
        if keyword:
            # Add a filter for keyword search in name and description
            keyword = f"%{keyword}%"  # Add wildcards for partial matching
            query = query.filter(
                (self.model.name.ilike(keyword)) |
                (self.model.description.ilike(keyword)) |
                (self.model.category_list.ilike(keyword)) |
                (self.model.website.ilike(keyword)) |
                (self.model.address.ilike(keyword))
            )
        # Add a filter to exclude businesses with is_active set to False
        query = query.filter(self.model.is_active == True)
        # Add a filter condition to exclude rooms where owner_id is null
        # query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(Business.images)).all()

    def search_all_businesses(self, db: Session, country: str = None, state: str = None, city: str = None,
                          category_list: str = None, is_online: bool = None) -> List[Type[Business]]:
        query = db.query(self.model)

        if country:
            query = query.filter(self.model.country == country)
        if state:
            query = query.filter(self.model.state == state)
        if city:
            query = query.filter(self.model.city == city)
        if category_list:
            # Filter businesses with categories that match any value in the provided category list
            query = query.filter(self.model.category_list == category_list)
        if is_online is not None:
            query = query.filter(self.model.is_online == is_online)

        return query.all()

    def get_by_owner_id(self, db: Session, owner_id: int) -> Optional[Business]:
        """
        Retrieve a business owned by a specific owner.
        :param db: Database session
        :param owner_id: The ID of the owner
        :return: Business object or None if not found
        """
        return db.query(self.model).filter(self.model.owner_id == owner_id).first()

    def update_business_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'business' in key:
                    try:
                        business_id = int(key.split("-")[1])  # Extract the business ID from the JSON key
                    # Extract the job ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    businesses = self.get(db, id=int(business_id))
                    if businesses:
                        if businesses:
                            if businesses.views is None:
                                businesses.views = 0
                        businesses.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    def update_images(self, db: Session, business_id: int, image_urls: List[str]) -> bool:
        try:
            business = self.get(db, id=business_id)
            if business:
                # Clear existing images associated with the business
                business.images = []
                for image_url in image_urls:
                    business_image = BusinessImage(image_url=image_url)
                    business.images.append(business_image)
                db.commit()
                return True
            return False
        except exc.SQLAlchemyError:
            db.rollback()
            return False
    
    def check_business_add_request(self, db: Session, place_id: str):
        request = db.query(BusinessRequest).filter(BusinessRequest.place_id == place_id).first()
        return request
    
    def create_business_add_request(self, db: Session, place_id: str, description: str):
        new_request = BusinessRequest(place_id=place_id, description=description)
        db.add(new_request)
        db.commit()
        db.refresh(new_request)        
        return new_request
    
    def update_business_request(self, db: Session, place_id: str, approved_status: str):
        request = db.query(BusinessRequest).filter(BusinessRequest.place_id == place_id).first()
        if request:
            request.approved_status = approved_status
            db.commit()
            db.refresh(request)
            return request
        return False


business = CRUDBusiness(Business)
