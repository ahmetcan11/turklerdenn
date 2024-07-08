from typing import List, Type, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, cast, Float
from crud.base import CRUDBase
from models.HouseImage import HouseImage  # Import your HouseImage model
from models.house import House  # Import your House model
from schemas.Housing.house_schema import HouseCreate, HouseBase  # Import your HouseCreate and HouseBase schemas
from models.IDGenerationService import id_service
from utils.common_util import get_coordinates_for_address


class CRUDHouse(CRUDBase[House, HouseCreate, HouseBase]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> House:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(House.images)).first()

    def create_with_owner(
            self, db: Session, *, obj_in: HouseCreate, owner_id: int, image_urls: List[str]
    ) -> House:
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
        house_data = {
            'title': obj_in_data.get('title'),
            'price': obj_in_data.get('price'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": latitude,
            "longitude": longitude,
            'square_feet': obj_in_data.get('square_feet'),  # Add squarefeet
            'description': obj_in_data.get('description'),
            'house_type': obj_in_data.get('house_type'),
            'owner_id': owner_id
        }
        db_obj = House(
            **house_data
        )
        for image_url in image_urls:
            house_image = HouseImage(image_url=image_url)
            db_obj.images.append(house_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "house-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Type[House]]:
        return (
            db.query(self.model)
            .filter(House.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_houses(
            self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
            city: Optional[str] = None, square_feet_min: Optional[int] = None,
            square_feet_max: Optional[int] = None,
            house_type: Optional[str] = None,
            bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
            tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
            keyword: str = None, sort_by_top_post: bool = False, sort_by_fresh_post: bool = False,
            skip: int = 0, limit: int = 100) -> List[Type[House]]:
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

        if square_feet_min != 0 or square_feet_max != 0:
            if square_feet_min is not None:
                query = query.filter(self.model.square_feet >= square_feet_min)

            if square_feet_max is not None:
                query = query.filter(self.model.square_feet <= square_feet_max)

        if house_type:
            query = query.filter(self.model.house_type == house_type)

        if keyword:
            # Add a filter for keyword search in name and description
            keyword = f"%{keyword}%"  # Add wildcards for partial matching
            query = query.filter(
                (self.model.address.ilike(keyword)) |
                (self.model.description.ilike(keyword)) |
                (self.model.title.ilike(keyword))
            )
        # Add a filter condition to exclude rooms where owner_id is nulll
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(House.images)).all()

    def update_house_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'house' in key:
                    try:
                        house_id = int(key.split("-")[1])  # Extract the house ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    house_obj = self.get(db, id=int(house_id))
                    if house_obj:
                        if house_obj:
                            if house_obj.views is None:
                                house_obj.views = 0
                        house_obj.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False



# Create an instance of CRUDHouseItem for reuse
house = CRUDHouse(House)
