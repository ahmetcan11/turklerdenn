from typing import List, Type, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, cast, Float
from crud.base import CRUDBase
from models.EventImage import EventImage
from models.event import Event  # Import your Event model
from schemas.Event.event import EventCreate, EventBase  # Import your EventCreate and EventUpdate schemas
from models.IDGenerationService import id_service
from datetime import datetime

from utils.common_util import get_coordinates_for_address


class CRUDEvent(CRUDBase[Event, EventCreate, EventBase]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> Event:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(Event.images)).first()

    def create_with_owner(
            self, db: Session, *, obj_in: EventCreate, owner_id: int, image_urls: List[str]
    ) -> Event:
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
        event_data = {
            'title': obj_in_data.get('title'),
            'description': obj_in_data.get('description'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": latitude,
            "longitude": longitude,
            'start_time': obj_in_data.get('start_time'),
            'online': obj_in_data.get('online'),
            'price': obj_in_data.get('price'),
            'owner_id': owner_id
        }
        db_obj = Event(
            **event_data
        )
        for image_url in image_urls:
            event_image = EventImage(image_url=image_url)
            db_obj.images.append(event_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "event-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Type[Event]]:
        return (
            db.query(self.model)
            .filter(Event.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_by_location(
            self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
            city: Optional[str] = None, start_time: Optional[str] = None,
            end_time: Optional[str] = None, keyword: str = None, sort_by_top_post: bool = False, sort_by_fresh_post: bool = False,
            bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
            tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
            skip: int = 0, limit: int = 100
    ) -> list[Type[Event]]:
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
        if keyword:
            # Add a filter for keyword search in name and description
            keyword = f"%{keyword}%"  # Add wildcards for partial matching
            query = query.filter(
                (self.model.address.ilike(keyword)) |
                (self.model.description.ilike(keyword)) |
                (self.model.title.ilike(keyword))
            )
        # Add a filter condition to exclude events where owner_id is null
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))

        if start_time and end_time:
            start_datetime = datetime.fromisoformat(start_time)
            end_datetime = datetime.fromisoformat(end_time)
            query = query.filter(self.model.start_time >= start_datetime, self.model.start_time <= end_datetime)

        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(Event.images)).all()

    def deactivate(self, db: Session, event_id: int) -> Optional[Event]:
        db_obj = self.get(db, id=event_id)
        if db_obj:
            db_obj.is_active = False
            db.commit()
            db.refresh(db_obj)
            return db_obj
        return None

    def update_event_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'event' in key:
                    try:
                        event_id = int(key.split("-")[1])  # Extract the house ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    event = self.get(db, id=int(event_id))
                    if event:
                        if event:
                            if event.views is None:
                                event.views = 0
                        event.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False


# Create an instance of CRUDEvent for reuse
crud_event = CRUDEvent(Event)
