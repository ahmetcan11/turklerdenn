from http.client import HTTPException
from typing import List, Type, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, cast, Float

from crud import crud_like, crud_comment
from crud.base import CRUDBase
from models.general import General, GeneralImage, Comment, Interest
from schemas.General.general_schema import GeneralCreate, GeneralBase, CommentCreate
from utils.common_util import get_coordinates_for_address


class CRUDGeneral(CRUDBase[General, GeneralCreate, GeneralBase]):

    def get_by_id(self, db: Session, *, id: int
                  ) -> General:
        query = db.query(self.model)
        query = query.filter(self.model.id == id)
        return query.options(joinedload(General.images)).first()

    def get_generals(
            self, db: Session, country: Optional[str] = None, state: Optional[str] = None,
            city: Optional[str] = None, interest_id: Optional[int] = None,
            keyword: str = None, sort_by_top_post: bool = False,
            sort_by_fresh_post: bool = False,
            bl_latitude: Optional[float] = None, bl_longitude: Optional[float] = None,
            tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
            skip: int = 0, limit: int = 100) -> List[Type[General]]:
        sort_style_top_post = self.model.upvote.desc()
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
                (self.model.description.ilike(keyword))
            )
        if interest_id:
            query = query.filter(General.interest_id == interest_id)
        # Add a filter condition to exclude rooms where owner_id is nulll
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        if sort_by_top_post:
            query = query.order_by(sort_style_top_post)
        elif sort_by_fresh_post:
            query = query.order_by(sort_style_fresh_post)
        return query.offset(skip).limit(limit).options(joinedload(General.images)).all()

    def get_generals2(
            self, db: Session, user_id: int, country: Optional[str] = None, state: Optional[str] = None,
            city: Optional[str] = None,
            keyword: str = None, sort_by_view: bool = False, skip: int = 0, limit: int = 100) -> List[Type[General]]:
        query = db.query(self.model)
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
                (self.model.description.ilike(keyword))
            )
        # Add a filter condition to exclude rooms where owner_id is nulll
        query = query.filter(self.model.owner_id.isnot(None))
        query = query.filter(self.model.post_id.isnot(None))
        sort_style = self.model.views.desc()
        if sort_by_view:
            query = query.order_by(sort_style)
        posts = query.offset(skip).limit(limit).options(joinedload(General.images)).all()
        result = []
        for post in posts:
            post_dict = post.__dict__.copy()  # Convert the SQLAlchemy model instance to a dictionary
            # Fetch like status
            up_down_obj = crud_like.get_liked_general(db=db, user_id=user_id, general_post_id=post.id)

            post_dict['upvoted'] = False
            post_dict['downvoted'] = False
            if up_down_obj:
                if up_down_obj.upvote:
                    post_dict['upvoted'] = True
                elif up_down_obj.downvote:
                    post_dict['downvoted'] = True

            # Exclude SQLAlchemy internal attribute
            post_dict.pop("_sa_instance_state", None)

            result.append(post_dict)

        return result

    def create_with_owner(
            self, db: Session, *, obj_in: GeneralCreate, owner_id: int, interest: str, image_urls: List[str] = None) -> General:
        # Get the interest ID based on the interest name received
        interest = db.query(Interest).filter(Interest.name == interest).first()
        if not interest:
            return {"error": "Invalid interest"}
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
            'description': obj_in_data.get('description'),
            'address': obj_in_data.get('address'),
            'country': obj_in_data.get('country'),
            'state': obj_in_data.get('state'),
            'city': obj_in_data.get('city'),
            "latitude": latitude,
            "longitude": longitude,
            'owner_id': owner_id,
            'interest_id': interest.id  # Assuming this field is passed in obj_in
        }
        db_obj = General(
            **item_data
        )
        if image_urls:
            for image_url in image_urls:
                general_image = GeneralImage(image_url=image_url)
                db_obj.images.append(general_image)

        db.add(db_obj)
        db.flush()  # Flush to generate the db_obj.id
        db_obj.post_id = "general-" + str(db_obj.id)
        db.commit()  # Commit everything in one go
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
            self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[General]:
        return (
            db.query(self.model)
            .filter(General.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_comment(self, db: Session, *, comment: CommentCreate, owner_id: int, post_id: int, first_name: str, last_name: str):
    # Get the general post from the database
        general_post = db.query(General).filter(General.id == post_id).first()
        comments = crud_comment.get_comments(db, general_post.id)
        comments_with_replies = []
        total_comments_count = len(comments)

        for comment in comments:
            comment_replies = crud_comment.get_comment_replies(db, comment.id)
            comment.replies = comment_replies
            total_comments_count += len(comment_replies)
            comments_with_replies.append(comment)
        if not general_post:
            raise HTTPException(status_code=404, detail="General post not found")

        # Initialize total_comments_count if it's null
        if general_post.total_comments_count is None:
            general_post.total_comments_count = 0

        # Increment the total_comments_count
        general_post.total_comments_count = total_comments_count + 1

        # Add the comment
        obj_in_data = jsonable_encoder(comment)
        comment_data = {
            'text': obj_in_data.get('comment'),
            "owner_name": first_name,
            "owner_last_name": last_name,
            'owner_id': owner_id,
            'post_id': post_id
        }
        db_obj = Comment(**comment_data)
        db.add(db_obj)

        # Commit the changes
        db.commit()
        db.refresh(db_obj)
        db.refresh(general_post)  # Refresh the general_post to reflect the updated comment count

        return db_obj


    def reply_to_comment(self,
                         db: Session,
                         *,
                         reply: CommentCreate,
                         owner_id: int,
                         parent_comment_id: int, first_name: str, last_name: str):
        parent_comment = db.query(Comment).filter(Comment.id == parent_comment_id).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")

        # Get the post_id from the parent comment
        post_id = parent_comment.post_id

        # Get the general post from the database
        general_post = db.query(General).filter(General.id == post_id).first()
        if not general_post:
            raise HTTPException(status_code=404, detail="General post not found")

        comments = crud_comment.get_comments(db, general_post.id)
        comments_with_replies = []
        total_comments_count = len(comments)

        for comment in comments:
            comment_replies = crud_comment.get_comment_replies(db, comment.id)
            comment.replies = comment_replies
            total_comments_count += len(comment_replies)
            comments_with_replies.append(comment)
        if not general_post:
            raise HTTPException(status_code=404, detail="General post not found")

        # Initialize total_comments_count if it's null
        if general_post.total_comments_count is None:
            general_post.total_comments_count = 0

        # Increment the total_comments_count
        general_post.total_comments_count = total_comments_count + 1
    
        obj_in_data = jsonable_encoder(reply)
        reply_data = {
            'text': obj_in_data.get('comment'),
            'owner_id': owner_id,
            "owner_name": first_name,
            "owner_last_name": last_name,
            'post_id': None,  # In a reply, post_id can be set to None as it's linked to the parent comment
            'parent_comment_id': parent_comment_id  # Link this reply to the parent comment
        }
        db_obj = Comment(
            **reply_data
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db.refresh(general_post)  # Refresh the general_post to reflect the updated comment count

        return db_obj


    def upvote_general_post(self, db: Session, *, general_post_id: int, user_id: int):
        general_post = db.query(General).filter(General.id == general_post_id).first()
        if general_post:
            general_post.upvote += 1
            db.commit()
            db.refresh(general_post)
            return general_post


    def remove_upvote_general_post(self, db: Session, *, general_post_id: int, user_id: int):
        general_post = db.query(General).filter(General.id == general_post_id).first()
        if general_post:
            general_post.upvote -= 1
            db.commit()
            db.refresh(general_post)
            return general_post

    def downvote_general_post(self, db: Session, *, general_post_id: int, user_id: int):
        general_post = db.query(General).filter(General.id == general_post_id).first()
        if general_post:
            general_post.downvote += 1
            db.commit()
            db.refresh(general_post)
            return general_post

    def remove_downvote_general_post(self, db: Session, *, general_post_id: int, user_id: int):
        general_post = db.query(General).filter(General.id == general_post_id).first()
        if general_post:
            general_post.downvote -= 1
            db.commit()
            db.refresh(general_post)
            return general_post

# Create an instance of CRUDFreeItem for reuse
crud_general = CRUDGeneral(General)
