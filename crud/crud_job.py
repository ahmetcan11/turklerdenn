from typing import List, Type, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, cast, Float
from crud.base import CRUDBase
from models.JobImage import JobImage
from models.job import Job  # Import your Job model
from schemas.Job.job import JobCreate, JobBase  # Import your JobCreate and JobUpdate schemas
from models.IDGenerationService import id_service
from utils.common_util import get_coordinates_for_address


class CRUDJob(CRUDBase[Job, JobCreate, JobBase]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> Job:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(Job.images)).first()

    def create_with_owner(
            self, db: Session, *, obj_in: JobCreate, owner_id: int
    , image_urls: List[str]) -> Job:
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

        item_data = {
            'title': obj_in_data.get('title'),
            'country': obj_in_data.get('country'),
            'address': obj_in_data.get('address'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": latitude,
            "longitude": longitude,
            'business_area': obj_in_data.get('business_area'),
            'work_type': obj_in_data.get('work_type'),
            'description': obj_in_data.get('description'),
            'owner_id': owner_id
        }
        db_obj = Job(
            **item_data
        )
        for image_url in image_urls:
            job_image = JobImage(image_url=image_url)
            db_obj.images.append(job_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "job-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Type[Job]]:
        return (
            db.query(self.model)
            .filter(Job.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


    def get_jobs_by_location(self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
         city: Optional[str] = None,
         keyword: str = None, sort_by_top_post: bool = False,
         sort_by_fresh_post: bool = False,
         bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
         tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
         skip: int = 0, limit: int = 100) -> list[Type[Job]]:
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
        # Add a filter condition to exclude rooms where owner_id is null
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(Job.images)).all()

    def update_job_views_from_json(self, db: Session, json_data: dict):
        try:
            for key, views in json_data.items():
                if 'job' in key:
                    try:
                        job_id = int(key.split("-")[1])  # Extract the job ID from the JSON key
                    except ValueError:
                        # Skip this item if conversion fails
                        continue
                    job = self.get(db, id=int(job_id))
                    if job:
                        if job:
                            if job.views is None:
                                job.views = 0
                        job.views += int(views)  # Update the views field
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False


# Create an instance of CRUDJob for reuse
crud_job = CRUDJob(Job)
