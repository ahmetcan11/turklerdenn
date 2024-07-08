from fastapi import APIRouter

from api.api_v1.endpoints import users, login, \
    shared_room, test_endpoints, free, event, house, \
    job, business, general, comment
from api.api_v1.endpoints.payments import paypal, stripe
from api.api_v1.endpoints.auth import auth_router
from api.api_v1.endpoints.google_analytics import google_analytics

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(test_endpoints.router, prefix="/test", tags=["test"])
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(shared_room.router, prefix="/shared_room", tags=["shared_room"])
# api_router.include_router(otp.router, prefix="/otp", tags=["otp"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(free.router, prefix="/free", tags=["free"])
api_router.include_router(event.router, prefix="/event", tags=["event"])
api_router.include_router(house.router, prefix="/house", tags=["house"])
api_router.include_router(job.router, prefix="/job", tags=["job"])
api_router.include_router(general.router, prefix="/general", tags=["general"])
api_router.include_router(comment.router, prefix="/comment", tags=["comment"])
api_router.include_router(paypal.router, prefix="/paypal", tags=["payment"])
api_router.include_router(stripe.router, prefix="/stripe", tags=["payment"])
api_router.include_router(google_analytics.router, prefix="/google_analytics", tags=["GA"])
