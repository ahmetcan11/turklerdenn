from sqlalchemy.orm import Session, joinedload
from models.otp import Codes
from datetime import datetime, timedelta


def create_reset_code(db: Session, email: str, reset_code: str):
    code = Codes(email=email, reset_code=reset_code, status='1', expired_in=datetime.utcnow())
    db.add(code)
    db.commit()
    db.refresh(code)  # Refresh the code object to get the updated values from the database
    return code


def check_reset_password_token(db: Session, reset_password_token: str):
    # Calculate the timestamp 10 minutes ago
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

    # Execute the query using SQLAlchemy's Session
    query = db.query(Codes).filter(
        Codes.status == '1',
        Codes.reset_code == reset_password_token,
        Codes.expired_in >= ten_minutes_ago
    )
    return query.first()  # Return the first matching row or None if not found


def disable_reset_code(db: Session, reset_password_token: str, email: str):
    # Find and update the Codes object matching the criteria
    code_to_disable = (
        db.query(Codes)
        .filter(
            Codes.status == '1',
            Codes.reset_code == reset_password_token,
            Codes.email == email
        )
        .first()
    )
    if code_to_disable:
        # Update the status to '9'
        code_to_disable.status = '9'
        db.commit()
        return True  # Indicate success
    else:
        return False  # Indicate that no matching object was found