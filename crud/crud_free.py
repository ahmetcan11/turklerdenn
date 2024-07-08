from typing import List, Type, Optional
from sqlalchemy import cast
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, Float, Numeric
from crud.base import CRUDBase
from models.FreeImage import FreeImage
from models.free import Free  # Import your Free model
from schemas.Free.free_schema import FreeCreate, FreeBase  # Import your FreeCreate and FreeUpdate schemas
from utils.common_util import get_coordinates_for_address
from models.IDGenerationService import id_service


class CRUDFreeItem(CRUDBase[Free, FreeCreate, FreeBase]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> Free:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(Free.images)).first()

    def create_with_owner(
            self, db: Session, *, obj_in: FreeCreate, owner_id: int
    , image_urls: List[str]) -> Free:
        obj_in_data = jsonable_encoder(obj_in)
        coordinates = get_coordinates_for_address(
            obj_in_data.get('address') + " " + obj_in_data.get('city') + " "
            + obj_in_data.get('state') + " " + obj_in_data.get('country'))
        item_data = {
            'title': obj_in_data.get('title'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": coordinates.get('latitude'),
            "longitude": coordinates.get('longitude'),
            'description': obj_in_data.get('description'),
            'owner_id': owner_id
        }
        db_obj = Free(
            **item_data
        )
        for image_url in image_urls:
            free_image = FreeImage(image_url=image_url)
            db_obj.images.append(free_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "free_item-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Type[Free]]:
        return (
            db.query(self.model)
            .filter(Free.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_items_by_location(self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
                              city: Optional[str] = None,
                              keyword: str = None,
                              bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
                              tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
                              sort_by_top_post: bool = False, sort_by_fresh_post: bool = False,
                              skip: int = 0, limit: int = 100) -> list[Type[Free]]:
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
        return query.offset(skip).limit(limit).options(joinedload(Free.images)).all()


    def get_items_by_coordinates(self, db: Session, bl_latitude: float, bl_longitude: float,
                              tr_latitude: float, tr_longitude: float,
                              keyword: str = None,  sort_by_view: bool = False, skip: int = 0, limit: int = 100) -> list[Type[Free]]:
        query = db.query(self.model).filter(
            cast(self.model.latitude, Float) >= bl_latitude,
            cast(self.model.latitude, Float) <= tr_latitude,
            cast(self.model.longitude, Float) >= bl_longitude,
            cast(self.model.longitude, Float) <= tr_longitude
        )
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        sort_style = self.model.views.desc()
        if sort_by_view:
            query = query.order_by(sort_style)
        return query.offset(skip).limit(limit).options(joinedload(Free.images)).all()


    def update_free_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'free_item' in key:
                    try:
                        free_id = int(key.split("-")[1])  # Extract the free ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    free = self.get(db, id=int(free_id))
                    if free:
                        if free:
                            if free.views is None:
                                free.views = 0
                        free.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False


# Create an instance of CRUDFreeItem for reuse
crud_free_item = CRUDFreeItem(Free)
