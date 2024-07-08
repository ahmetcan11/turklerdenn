from apscheduler.schedulers.background import BackgroundScheduler
from api import deps
from sqlalchemy.orm import Session
from fastapi import Depends
from api.deps import get_db
from utils.updateViewsTask import update_views
from utils.googleAnalytics import write_unique_users_to_file

scheduler = BackgroundScheduler()
scheduler.add_job(write_unique_users_to_file, 'interval', seconds=28800)
