import os
import requests
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from models.general import Interest
from schemas.User import user_schema
from models.user import User as user_model
from crud import crud_user, crud_business, crud_shared_room, crud_free, crud_event, crud_house, crud_job, crud_general, \
    crud_comment, crud_like
from api import deps
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from enum import Enum
from fastapi import Query
from utils.updateViewsTask import update_views
router = APIRouter()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'cert/fluent-horizon-388119-51be586f53a0.json'
templates = Jinja2Templates(directory="templates")


def load_sample_terms(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


# Load sample terms from the text file
sample_terms = load_sample_terms("utils/business_values.txt")


def search_similar_terms(query, terms, threshold=70, limit=8):
    # Normalize query by removing non-alphanumeric characters and converting to lowercase
    normalized_query = re.sub(r'\W+', ' ', query).lower()
    # Search for similar terms
    # Filter terms that have a similarity score above the threshold
    similar_terms = process.extract(normalized_query, terms, scorer=fuzz.partial_ratio, limit=limit)
    filtered_terms = [term for term, score in similar_terms if score >= threshold]
    if not filtered_terms:
        return {"message": "No similar terms found."}
    return filtered_terms


@router.get("/search_terms_algorithm/")
async def search_terms(query: str = Query(..., description="Search query")):
    similar_terms = search_similar_terms(query, sample_terms)
    if not similar_terms:
        return {"message": "No similar terms found."}
    return similar_terms

@router.get("/dum")
async def search_terms(*,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user)):
    public_profile = get_public_user_profile(current_user.id, db)
    return public_profile.get("first_name")

@router.get("/searchBusinesses", include_in_schema=False)
def search_businesses(
        business_id: int,
        db: Session = Depends(deps.get_db)
):
    businesses = crud_business.business.get(db, business_id)
    return businesses

class SearchType(str, Enum):
    BUSINESS = "business"
    SHARED_ROOM = "shared_room"
    EVENT = "event"
    FREE_ITEM = "free_item"
    HOUSE = "house"
    JOB = "job"
    GENERAL = "general"
    ALL_MARKETPLACE = "all_marketplace"


class SearchQuery(BaseModel):
    search_type: SearchType
    keyword: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    interest: Optional[str] = None
    is_online: Optional[bool] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    furniture_available: Optional[bool] = None
    house_type: Optional[str] = None
    square_feet_min: Optional[int] = None
    square_feet_max: Optional[int] = None


def get_results_query(db: Session, search_type: SearchType, country: str, state: str, city: str, category: str, is_online: bool, keyword: str, furniture_available: bool, house_type: str, square_feet_min: int, square_feet_max: int, start_time: str, end_time: str, sort_by_view: bool) -> Any:
    if search_type == SearchType.BUSINESS:
        return crud_general.crud_general.search_businesses(db=db, country=country, state=state, city=city, category_list=[category], is_online=is_online, keyword=keyword, sort_by_view=sort_by_view)
    elif search_type == SearchType.SHARED_ROOM:
        return crud_general.crud_general.search_shared_rooms(db=db, country=country, state=state, city=city, furniture_available=furniture_available, keyword=keyword, sort_by_view=sort_by_view)
    elif search_type == SearchType.FREE_ITEM:
        return crud_free.crud_free_item.get_items_by_location(db=db, country=country, state=state, city=city, keyword=keyword, sort_by_view=sort_by_view)
    elif search_type == SearchType.EVENT:
        return crud_event.crud_event.get_events_by_location(db=db, country=country, state=state, city=city, start_time=start_time, end_time=end_time, keyword=keyword, sort_by_view=sort_by_view)
    elif search_type == SearchType.HOUSE:
        return crud_house.house.get_houses(db=db, country=country, state=state, city=city, square_feet_max=square_feet_max, square_feet_min=square_feet_min, house_type=house_type, keyword=keyword, sort_by_view=sort_by_view)
    elif search_type == SearchType.JOB:
        return crud_job.crud_job.get_jobs_by_location(db=db, country=country, state=state, city=city, keyword=keyword, sort_by_view=sort_by_view)
    else:
        raise HTTPException(status_code=400, detail="Invalid search type")


@router.post("/search")
def search(query: SearchQuery, db: Session = Depends(deps.get_db), bl_latitude: Optional[float] = None,
           bl_longitude: Optional[float] = None,
           tr_latitude: Optional[float] = None, tr_longitude: Optional[float] = None,
           sort_by_top_post: bool = False, sort_by_fresh_post: bool = False, skip: int = 0,
    limit: int = 100,
           ):
    """
    Search Type :"all_marketplace","business", "shared_room", "event", "free_item", "job"
    , "house", "general"
    IMMIGRATION = 1 ,TRAVEL = 2, FOOD = 3, CARS = 4, GROUP_CHATS = 5
    IT = 6, RANDOM = 7, FOOD_DELIVERY_APPS = 8, E_COMMERCE = 9
    """
    search_type = query.search_type
    category = query.category
    country = query.country
    state = query.state
    city = query.city
    interest = query.interest
    is_online = query.is_online
    keyword = query.keyword
    similar_terms = None
    furniture_available = query.furniture_available
    house_type = query.house_type
    square_feet_min = query.square_feet_min
    square_feet_max = query.square_feet_max
    start_time = query.start_time
    end_time = query.end_time
    results = []

    try:
        interest_id = int(interest)  # Convert the interest to an integer
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid interest ID")
    
    interest = db.query(Interest).filter(Interest.id == interest).first()
    if interest:
        interest_id = interest.id
    else:
        interest_id = None
    if search_type == SearchType.ALL_MARKETPLACE:
        # Define default values for filters
        country_filter = country or None
        state_filter = state or None
        city_filter = city or None
        # Fetch all results for each search type with the specified filters
        results.extend(
            crud_business.business.search_businesses(
                # call places api and get businesses in this range.
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                category_list=similar_terms,
                is_online=is_online,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_shared_room.shared_room.get_rooms_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                furniture_available=furniture_available,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_free.crud_free_item.get_items_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_event.crud_event.get_events_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_house.house.get_houses(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                square_feet_max=square_feet_max,
                square_feet_min=square_feet_min,
                house_type=house_type,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_job.crud_job.get_jobs_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )

    elif search_type == SearchType.BUSINESS:
        if not category:  # Check if category is empty
            category = "all_marketplace"
        if category:
            if category.lower() == "all_marketplace":
                results = crud_business.business.search_businesses(
                    db=db,
                    country=country,
                    state=state,
                    city=city,
                    bl_latitude=bl_latitude,
                    bl_longitude=bl_longitude,
                    tr_latitude=tr_latitude,
                    tr_longitude=tr_longitude,
                    is_online=is_online,
                    keyword=keyword,
                    sort_by_top_post=sort_by_top_post,
                    sort_by_fresh_post=sort_by_fresh_post,
                    skip=skip,
                    limit=limit
                )
            else:
                similar_terms = search_similar_terms(category, sample_terms)
                results = crud_business.business.search_businesses(
                    db=db,
                    country=country,
                    state=state,
                    city=city,
                    bl_latitude=bl_latitude,
                    bl_longitude=bl_longitude,
                    tr_latitude=tr_latitude,
                    tr_longitude=tr_longitude,
                    category_list=similar_terms,
                    is_online=is_online,
                    keyword=keyword,
                    sort_by_top_post=sort_by_top_post,
                    sort_by_fresh_post=sort_by_fresh_post,
                    skip=skip,
                    limit=limit
                )
    elif search_type == SearchType.SHARED_ROOM:
        results = crud_shared_room.shared_room.get_rooms_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            bl_latitude=bl_latitude,
            bl_longitude=bl_longitude,
            tr_latitude=tr_latitude,
            tr_longitude=tr_longitude,
            furniture_available=furniture_available,
            keyword=keyword,
            sort_by_top_post=sort_by_top_post,
            sort_by_fresh_post=sort_by_fresh_post,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.FREE_ITEM:
        results = crud_free.crud_free_item.get_items_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            bl_latitude=bl_latitude,
            bl_longitude=bl_longitude,
            tr_latitude=tr_latitude,
            tr_longitude=tr_longitude,
            keyword=keyword,
            sort_by_top_post=sort_by_top_post,
            sort_by_fresh_post=sort_by_fresh_post,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.EVENT:
        results = crud_event.crud_event.get_events_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            bl_latitude=bl_latitude,
            bl_longitude=bl_longitude,
            tr_latitude=tr_latitude,
            tr_longitude=tr_longitude,
            start_time=start_time,
            end_time=end_time,
            keyword=keyword,
            sort_by_top_post=sort_by_top_post,
            sort_by_fresh_post=sort_by_fresh_post,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.HOUSE:
        if house_type == "house_all":
            house_type = None
        results = crud_house.house.get_houses(
            db=db,
            country=country,
            state=state,
            city=city,
            bl_latitude=bl_latitude,
            bl_longitude=bl_longitude,
            tr_latitude=tr_latitude,
            tr_longitude=tr_longitude,
            square_feet_max=square_feet_max,
            square_feet_min=square_feet_min,
            house_type=house_type,
            keyword=keyword,
            sort_by_top_post=sort_by_top_post,
            sort_by_fresh_post=sort_by_fresh_post,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.JOB:
        results = crud_job.crud_job.get_jobs_by_location(
                db=db,
                country=country,
                state=state,
                city=city,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                keyword=keyword,
                sort_by_top_post=sort_by_top_post,
                sort_by_fresh_post=sort_by_fresh_post,
                skip=skip,
                limit=limit
            )
    elif search_type == SearchType.GENERAL:
        results = crud_general.crud_general.get_generals(
                db=db,
                country=country,
                state=state,
                city=city,
                bl_latitude=bl_latitude,
                bl_longitude=bl_longitude,
                tr_latitude=tr_latitude,
                tr_longitude=tr_longitude,
                interest_id=interest_id,
                keyword=keyword,
                sort_by_top_post=sort_by_top_post,
                sort_by_fresh_post=sort_by_fresh_post,
                skip=skip,
                limit=limit
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid search type")

    return results


@router.post("/search_authed")
def search(query: SearchQuery, db: Session = Depends(deps.get_db),
           sort_by_view: bool = True, skip: int = 0,
    limit: int = 100, current_user: Optional[user_model] = Depends(deps.get_current_active_alternate_user),
           ):
    """
    Search Type :"all","business", "shared_room", "event", "free_item", "job"
    , "house", "general"
    """
    search_type = query.search_type
    category = query.category
    country = query.country
    state = query.state
    city = query.city
    is_online = query.is_online
    keyword = query.keyword
    similar_terms = None
    furniture_available = query.furniture_available
    house_type = query.house_type
    square_feet_min = query.square_feet_min
    square_feet_max = query.square_feet_max
    start_time = query.start_time
    end_time = query.end_time
    results = []
    if search_type == SearchType.ALL:
        # Define default values for filters
        country_filter = country or None
        state_filter = state or None
        city_filter = city or None
        # Fetch all results for each search type with the specified filters
        results.extend(
            crud_business.business.search_businesses(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                category_list=similar_terms,
                is_online=is_online,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_shared_room.shared_room.get_rooms_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                furniture_available=furniture_available,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_free.crud_free_item.get_items_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_event.crud_event.get_events_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_house.house.get_houses(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                square_feet_max=square_feet_max,
                square_feet_min=square_feet_min,
                house_type=house_type,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )
        results.extend(
            crud_job.crud_job.get_jobs_by_location(
                db=db,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )

        results.extend(
        crud_general.crud_general.get_generals2(
                db=db,
                user_id=current_user.id,
                country=country_filter,
                state=state_filter,
                city=city_filter,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
        )

    elif search_type == SearchType.BUSINESS:
        if not category:  # Check if category is empty
            category = "all"
        if category:
            if category.lower() == "all":
                results = crud_business.business.search_businesses(
                    db=db,
                    country=country,
                    state=state,
                    city=city,
                    is_online=is_online,
                    keyword=keyword,
                    sort_by_view=sort_by_view,
                    skip=skip,
                    limit=limit
                )
            else:
                similar_terms = search_similar_terms(category, sample_terms)
                results = crud_business.business.search_businesses(
                    db=db,
                    country=country,
                    state=state,
                    city=city,
                    category_list=similar_terms,
                    is_online=is_online,
                    keyword=keyword,
                    sort_by_view=sort_by_view,
                    skip=skip,
                    limit=limit
                )
    elif search_type == SearchType.SHARED_ROOM:
        results = crud_shared_room.shared_room.get_rooms_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            furniture_available=furniture_available,
            keyword=keyword,
            sort_by_view=sort_by_view,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.FREE_ITEM:
        results = crud_free.crud_free_item.get_items_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            keyword=keyword,
            sort_by_view=sort_by_view,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.EVENT:
        results = crud_event.crud_event.get_events_by_location(
            db=db,
            country=country,
            state=state,
            city=city,
            start_time=start_time,
            end_time=end_time,
            keyword=keyword,
            sort_by_view=sort_by_view,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.HOUSE:
        if house_type == "house_all":
            house_type = None
        results = crud_house.house.get_houses(
            db=db,
            country=country,
            state=state,
            city=city,
            square_feet_max=square_feet_max,
            square_feet_min=square_feet_min,
            house_type=house_type,
            keyword=keyword,
            sort_by_view=sort_by_view,
            skip=skip,
            limit=limit
        )
    elif search_type == SearchType.JOB:
        results = crud_job.crud_job.get_jobs_by_location(
                db=db,
                country=country,
                state=state,
                city=city,
                keyword=keyword,
                sort_by_view=sort_by_view,
                skip=skip,
                limit=limit
            )
    elif search_type == SearchType.GENERAL:
        results = crud_general.crud_general.get_generals2(
                db=db,
                user_id=current_user.id,
                country=country,
                state=state,
                city=city,
                keyword=keyword,
                skip=skip,
                limit=limit
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid search type")

    return results

# @router.post("/posts/")
# def post_detail(request_body: dict,db: Session = Depends(deps.get_db)):
#     """
#     Search Type:, {"detail_id":"business-n"}, "shared_room-n", "event-n", "free_item-n", "house-n", "job-n", "general-n"
#     """
#     post_id = request_body.get("detail_id")
#     if not post_id:
#         raise HTTPException(status_code=400, detail="detail_id is required")

#     search_type, detail_id = post_id.split('-')
#     if search_type == SearchType.BUSINESS:
#         results = crud_business.business.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.SHARED_ROOM:
#         results = crud_shared_room.shared_room.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.FREE_ITEM:
#         results = crud_free.crud_free_item.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.EVENT:
#         results = crud_event.crud_event.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.HOUSE:
#         results = crud_house.house.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.JOB:
#         results = crud_job.crud_job.get_by_id(
#             db=db,
#             id=detail_id
#         )
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results = [{
#             'results': results,
#             'public_profile': public_profile
#         }]
#     elif search_type == SearchType.GENERAL:
#         results = crud_general.crud_general.get_by_id(db, id=detail_id)
#         comments = crud_comment.get_comments(db, results.id)
#         comments_with_replies = []

#         for comment in comments:
#             comment.replies = crud_comment.get_comment_replies(db, comment.id)
#             comments_with_replies.append(comment)
#         public_profile = get_public_user_profile(results.owner_id, db)
#         results.upvote = results.upvote - results.downvote
#         results = [{
#             'results': results,
#             'comments': comments_with_replies,
#             'public_profile': public_profile
#         }]
#     else:
#         raise HTTPException(status_code=400, detail="Invalid search type")

#     return results

@router.post("/posts/")
def post_detail(request_body: dict, db: Session = Depends(deps.get_db)):
    """
    Search Type:, {"detail_id":"business-n"}, "shared_room-n", "event-n", "free_item-n", "house-n", "job-n", "general-n"
    """
    post_id = request_body.get("detail_id")
    if not post_id:
        raise HTTPException(status_code=400, detail="detail_id is required")

    search_type, detail_id = post_id.split('-')
    results = None
    public_profile = None

    try:
        if search_type == SearchType.BUSINESS:
            results = crud_business.business.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.SHARED_ROOM:
            results = crud_shared_room.shared_room.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.FREE_ITEM:
            results = crud_free.crud_free_item.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.EVENT:
            results = crud_event.crud_event.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.HOUSE:
            results = crud_house.house.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.JOB:
            results = crud_job.crud_job.get_by_id(db=db, id=detail_id)
        elif search_type == SearchType.GENERAL:
            results = crud_general.crud_general.get_by_id(db=db, id=detail_id)
            comments = crud_comment.get_comments(db, results.id)
            comments_with_replies = []
            total_comments_count = len(comments)

            for comment in comments:
                comment_replies = crud_comment.get_comment_replies(db, comment.id)
                comment.replies = comment_replies
                total_comments_count += len(comment_replies)
                comments_with_replies.append(comment)

            if results:
                results.upvote = results.upvote - results.downvote
                public_profile = get_public_user_profile(results.owner_id, db) if results.owner_id else None
                results = [{
                    'results': results,
                    'comments': comments_with_replies,
                    'comments_count': total_comments_count,
                    'public_profile': public_profile
                }]
            else:
                results = [{
                    'results': results,
                    'comments': comments_with_replies,
                    'comments_count': total_comments_count,
                    'public_profile': public_profile
                }]
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")

        if results and hasattr(results, 'owner_id') and results.owner_id:
            public_profile = get_public_user_profile(results.owner_id, db)

        return [{
            'results': results,
            'public_profile': public_profile
        }]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def get_public_user_profile(
    id,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.user.get(db, id=id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_public = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tel_number": user.tel_number,
        "whatsapp_number": user.whatsapp_number
        }
    return user_public


@router.get("/profile")
def read_user_by_id(
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.user.get(db, id=current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    all_posts = []
    all_posts.extend(user.free_items)
    all_posts.extend(user.events)
    all_posts.extend(user.shared_rooms)
    all_posts.extend(user.houses)
    all_posts.extend(user.jobs)
    all_posts.sort(key=lambda post: post.created_on, reverse=True)
    latest_posts = all_posts[:6]
    # Initialize total_views to 0
    total_views = 0

    # Sum up views from different categories
    def add_views(item):
        nonlocal total_views
        total_views += item.views or 0

    # Sum up views from different categories
    for business in user.businesses:
        add_views(business)
    for free_item in user.free_items:
        add_views(free_item)
    for event in user.events:
        add_views(event)
    for shared_room in user.shared_rooms:
        add_views(shared_room)
    for house in user.houses:
        add_views(house)
    for job in user.jobs:
        add_views(job)
    user_public = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tel_number": user.tel_number,
        "whatsapp_number": user.whatsapp_number,
        "total_views": total_views,
        "businesses": [
            {
                "id": business.id,
                "name": business.name,
                "country": business.country,
                "state": business.state,
                "city": business.city,
                "category_list": business.category_list,
                "description": business.description,
                "image_urls": [image.image_url for image in business.images],  # List of image URLs
                "website": business.website,
                "tel_number": business.tel_number,
                "whatsapp_number": business.whatsapp_number,
                "created_on": business.created_on,
                "is_active": business.is_active
            }
            for business in user.businesses if business.is_active  # Filter out inactive businesses
        ],
        "free_items": [
            {
                "id": free_item.id,
                "title": free_item.title,
                "country": free_item.country,
                "state": free_item.state,
                "city": free_item.city,
                "description": free_item.description,
                "image_urls": [image.image_url for image in free_item.images],  # List of image URLs
                "created_on": free_item.created_on
            }
            for free_item in user.free_items
        ],
        "events": [
            {
                "id": event.id,
                "title": event.title,
                "country": event.country,
                "state": event.state,
                "city": event.city,
                "start_time": event.start_time,
                "online": event.online,
                "price": event.price,
                "owner_id": event.owner.id,
                "description": event.description,
                "image_urls": [image.image_url for image in event.images],  # List of image URLs
                "created_on": event.created_on
            }
            for event in user.events
        ],
        "shared_rooms": [
            {
                "id": shared_room.id,
                "title": shared_room.title,
                "country": shared_room.country,
                "state": shared_room.state,
                "city": shared_room.city,
                "price": shared_room.price,
                "owner_id": shared_room.owner.id,
                "description": shared_room.description,
                "image_urls": [image.image_url for image in shared_room.images],  # List of image URLs
                "created_on": shared_room.created_on,
                "furniture_available": shared_room.furniture_available
            }
            for shared_room in user.shared_rooms
        ],
        "houses": [
            {
                "id": house.id,
                "title": house.title,
                "price": house.price,
                "square_feet": house.square_feet,
                "country": house.country,
                "state": house.state,
                "city": house.city,
                "owner_id": house.owner.id,
                "description": house.description,
                "image_urls": [image.image_url for image in house.images],  # List of image URLs
                "created_on": house.created_on
            }
            for house in user.houses
        ],
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "country": job.country,
                "state": job.state,
                "city": job.city,
                "owner_id": job.owner.id,
                "business_area": job.business_area,
                "work_type": job.work_type,
                "image_urls": [image.image_url for image in job.images],  # List of image URLs
                "created_on": job.created_on
            }
            for job in user.jobs
        ],
        "generals": [
            {
                "id": generals.id,
                "description": generals.description,
                "country": generals.country,
                "state": generals.state,
                "city": generals.city,
                "owner_id": generals.owner.id,
                "image_urls": [image.image_url for image in generals.images],  # List of image URLs
                "created_on": generals.created_on,
                "views": generals.views,
                "upvote": generals.upvote,
                "downvote": generals.downvote
            }
            for generals in user.generals
        ],
        "all_posts": [
            {
                "id": post.id,
                "post_id": post.post_id,
                "title": getattr(post, 'title', "No Title"),
                "description": post.description,
                "created_on": post.created_on,
                "image_urls": [image.image_url for image in post.images]
            }
            for post in latest_posts
        ],
        }
    return user_public


@router.get("/publicProfile/{user_id}")
def get_public_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    all_posts = []
    all_posts.extend(user.free_items)
    all_posts.extend(user.events)
    all_posts.extend(user.shared_rooms)
    all_posts.extend(user.houses)
    all_posts.extend(user.jobs)
    all_posts.extend(user.generals)
    all_posts.sort(key=lambda post: post.created_on, reverse=True)
    latest_posts = all_posts[:6]
    # Initialize total_views to 0
    total_views = 0
    # Sum up views from different categories

    def add_views(item):
        nonlocal total_views
        total_views += item.views or 0

    # Sum up views from different categories
    for business in user.businesses:
        add_views(business)
    for free_item in user.free_items:
        add_views(free_item)
    for event in user.events:
        add_views(event)
    for shared_room in user.shared_rooms:
        add_views(shared_room)
    for house in user.houses:
        add_views(house)
    for job in user.jobs:
        add_views(job)
    for generals in user.generals:
        add_views(generals)
    user_public = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tel_number": user.tel_number,
        "whatsapp_number": user.whatsapp_number,
        "total_views": total_views,
        "businesses": [
            {
                "id": business.id,
                "name": business.name,
                "country": business.country,
                "state": business.state,
                "city": business.city,
                "category_list": business.category_list,
                "description": business.description,
                "image_urls": [image.image_url for image in business.images],  # List of image URLs
                "website": business.website,
                "tel_number": business.tel_number,
                "whatsapp_number": business.whatsapp_number,
                "created_on": business.created_on,
                "is_active": business.is_active
            }
            for business in user.businesses if business.is_active  # Filter out inactive businesses
        ],
        "free_items": [
            {
                "id": free_item.id,
                "title": free_item.title,
                "country": free_item.country,
                "state": free_item.state,
                "city": free_item.city,
                "description": free_item.description,
                "image_urls": [image.image_url for image in free_item.images],  # List of image URLs
                "created_on": free_item.created_on
            }
            for free_item in user.free_items
        ],
        "events": [
            {
                "id": event.id,
                "title": event.title,
                "country": event.country,
                "state": event.state,
                "city": event.city,
                "start_time": event.start_time,
                "online": event.online,
                "price": event.price,
                "owner_id": event.owner.id,
                "description": event.description,
                "image_urls": [image.image_url for image in event.images],  # List of image URLs
                "created_on": event.created_on
            }
            for event in user.events
        ],
        "shared_rooms": [
            {
                "id": shared_room.id,
                "title": shared_room.title,
                "country": shared_room.country,
                "state": shared_room.state,
                "city": shared_room.city,
                "price": shared_room.price,
                "owner_id": shared_room.owner.id,
                "description": shared_room.description,
                "image_urls": [image.image_url for image in shared_room.images],  # List of image URLs
                "created_on": shared_room.created_on,
                "furniture_available": shared_room.furniture_available
            }
            for shared_room in user.shared_rooms
        ],
        "houses": [
            {
                "id": house.id,
                "title": house.title,
                "price": house.price,
                "square_feet": house.square_feet,
                "country": house.country,
                "state": house.state,
                "city": house.city,
                "owner_id": house.owner.id,
                "description": house.description,
                "image_urls": [image.image_url for image in house.images],  # List of image URLs
                "created_on": house.created_on
            }
            for house in user.houses
        ],
        "jobs": [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "country": job.country,
                "state": job.state,
                "city": job.city,
                "owner_id": job.owner.id,
                "business_area": job.business_area,
                "work_type": job.work_type,
                "image_urls": [image.image_url for image in job.images],  # List of image URLs
                "created_on": job.created_on
            }
            for job in user.jobs
        ],
        "generals": [
            {
                "id": generals.id,
                "description": generals.description,
                "country": generals.country,
                "state": generals.state,
                "city": generals.city,
                "owner_id": generals.owner.id,
                "image_urls": [image.image_url for image in generals.images],  # List of image URLs
                "created_on": generals.created_on,
                "views": generals.views,
                "upvote": generals.upvote,
                "downvote": generals.downvote
            }
            for generals in user.generals
        ],
        "all_posts": [
            {
                "id": post.id,
                "post_id": post.post_id,
                "title": getattr(post, 'title', "No Title"),
                "description": post.description,
                "created_on": post.created_on,
                "image_urls": [image.image_url for image in post.images]
            }
            for post in latest_posts
        ],
        }
    return user_public


@router.delete("/deletePost")
def delete_post(
    post_type: str,
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: user_model = Depends(deps.get_current_active_user),
) -> Any:
    """
        Post Type :"shared_room", "event", "free_item", "job"
        , "house", "general"
   """
    crud_classes = {
        "event": crud_event.crud_event,
        "free_item": crud_free.crud_free_item,
        "shared_room": crud_shared_room.shared_room,
        "house": crud_house.house,
        "job": crud_job.crud_job,
        "general": crud_general.crud_general
    }

    # Check if the post_type is valid and get the corresponding CRUD class
    if post_type not in crud_classes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post type.")

    crud_class = crud_classes[post_type]

    # Retrieve the post from the database
    post_in_db = crud_class.get(db, id=post_id)

    if not post_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{post_type.capitalize()} post not found",
        )
    if post_in_db.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not authorized to delete this {post_type}",
        )

    # Perform the delete operation
    deleted_item = crud_class.remove(db, id=post_id)
    return deleted_item

@router.get("/getAllUsers", response_model=List[user_schema.User], include_in_schema=False)
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Retrieve users.
    """
    user_check = crud_user.user.get_multi(db, skip=skip, limit=limit)
    return user_check


@router.get("/getAllBusinesses", include_in_schema=False)
def search_businesses(
        category: Optional[str] = None,
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        is_online: Optional[bool] = None,
        db: Session = Depends(deps.get_db)
):
    businesses = crud_business.business.search_all_businesses(
        db=db,
        country=country,
        state=state,
        city=city,
        category_list=category,  # We will search based on similar_terms only
        is_online=is_online
    )
    return businesses


class User(BaseModel):
    username: str
    email: str
    age: int


def get_paypal_access_token(client_id: str, client_secret: str) -> str:
    # Set up the request
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
        "content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    auth = (client_id, client_secret)

    # Send the request
    response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", data=data, headers=headers, auth=auth)

    # Parse the response
    response_json = response.json()
    if response.status_code == 200:
        # Access token retrieved successfully, return the token
        return response_json["access_token"]
    else:
        # Retrieving access token failed, raise an exception
        raise Exception(response_json["error_description"])

