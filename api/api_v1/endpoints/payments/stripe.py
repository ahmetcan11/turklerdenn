from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api import deps
from payments import handle_stripe
from crud import crud_business


router = APIRouter()


@router.get("/create_stripe_payment/{business_id}")
def create_business_no_user_stripe(business_id: int):
    # warning here
    session_object = handle_stripe.create_session_business("price_1OVWLpEfC3oh3lZNzK1dWwTs", business_id)
    checkout_url = session_object.url
    return {checkout_url: session_object.id}


@router.post("/verify_stripe_payment/{session_id}/{business_id}")
def create_business_no_user_stripe(session_id: str, business_id: int,
                                   db: Session = Depends(deps.get_db)):
    message = handle_stripe.get_session_info(session_id)
    payment_status = message.get("payment_status")
    metadata = message.get("metadata")
    business_id_meta = metadata.get("business_id")
    if business_id_meta:
        try:
            if not business_id == int(business_id_meta):
                raise HTTPException(status_code=403, detail=f"Invalid business id")
        except ValueError:
            # Handle the case where the conversion to an integer fails
            print("Invalid business_id format")
    if payment_status == "paid":
        business_activated = crud_business.business.activate(db, business_id)
        return {"business_activated_id": business_activated.id,
                "business_activated_name": business_activated.name}

    else:
        # Payment execution failed, raise an exception or handle accordingly
        raise HTTPException(status_code=400, detail=f"Payment execution failed go back to payment page")


@router.get("/success", include_in_schema=False)
def payment_successful():
    return "success"


@router.get("/cancel", include_in_schema=False)
def payment_cancel():
    return "cancel"
