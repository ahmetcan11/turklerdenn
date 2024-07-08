from typing import Any, Dict, Optional, Union, List, Type

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, Float, cast
from core.security import get_password_hash, verify_password
from crud.base import CRUDBase
from schemas.Housing.shared_room import SharedRoomCreate, SharedRoomUpdate
from models.sharedroom import SharedRoom
from models.sharedroomimage import SharedRoomImage
from models.IDGenerationService import id_service
from utils.common_util import get_coordinates_for_address


class CRUDSharedRoom(CRUDBase[SharedRoom, SharedRoomCreate, SharedRoomUpdate]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> SharedRoom:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(SharedRoom.images)).first()

    def create_with_owner(
            self, db: Session, *, obj_in: SharedRoomCreate, owner_id: int, image_urls: List[str]
    ) -> SharedRoom:
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

        room_data = {
            'title': obj_in_data.get('title'),
            'price': obj_in_data.get('price'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": latitude,
            "longitude": longitude,
            'description': obj_in_data.get('description'),
            'furniture_available': obj_in_data.get('furniture_available'),
            'owner_id': owner_id
        }
        db_obj = SharedRoom(
            **room_data
        )
        for image_url in image_urls:
            event_image = SharedRoomImage(image_url=image_url)
            db_obj.images.append(event_image)
        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "shared_room-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[SharedRoom]:
        return (
            db.query(self.model)
            .filter(SharedRoom.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def is_active(self, room_check: SharedRoom) -> bool:
        return room_check.is_active

    def get_rooms_by_location(self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
                              city: Optional[str] = None,
                              furniture_available: Optional[bool] = None,
                              bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
                              tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
                              keyword: str = None, sort_by_top_post: bool = False, sort_by_fresh_post: bool = False,
                              skip: int = 0, limit: int = 100) -> List[Type[SharedRoom]]:
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
        if furniture_available is not None:
            query = query.filter(self.model.furniture_available == furniture_available)
        # Add a filter condition to exclude rooms where owner_id is null
        if keyword:
            # Add a filter for keyword search in name and description
            keyword = f"%{keyword}%"  # Add wildcards for partial matching
            query = query.filter(
                (self.model.address.ilike(keyword)) |
                (self.model.description.ilike(keyword)) |
                (self.model.title.ilike(keyword))
            )
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(SharedRoom.images)).all()

    def update_shared_room_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'shared_room' in key:
                    try:
                        shared_room_id = int(key.split("-")[1])  # Extract the shared_room ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    shared_room_obj = self.get(db, id=int(shared_room_id))
                    if shared_room_obj:
                        if shared_room_obj.views is None:
                            shared_room_obj.views = 0
                        shared_room_obj.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False


shared_room = CRUDSharedRoom(SharedRoom)
