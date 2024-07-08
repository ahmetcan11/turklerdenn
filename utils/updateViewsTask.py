import os
import time

from crud import crud_business, crud_job, crud_shared_room, crud_house, crud_event, crud_free
import json
from sqlalchemy.orm import Session
from datetime import date
from api.deps import get_db
from datetime import date, timedelta


def update_views(aggregated_data):
    db: Session = next(get_db())
    # today = date.today()
    # yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    # json_file_path = f'views/{yesterday}.json'
    # if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
    #     json_dict = read_json_file(json_file_path)
    # else:
    #     print("File not found or is empty, retrying...")
    #     # Optionally add retry logic or a delay
    #     time.sleep(1)
    #     update_views()
    crud_business.business.update_business_views_from_json(db, aggregated_data)
    crud_job.crud_job.update_job_views_from_json(db, aggregated_data)
    crud_shared_room.shared_room.update_shared_room_views_from_json(db, aggregated_data)
    crud_free.crud_free_item.update_free_views_from_json(db, aggregated_data)
    crud_house.house.update_house_views_from_json(db, aggregated_data)
    crud_event.crud_event.update_event_views_from_json(db, aggregated_data)


def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return None
