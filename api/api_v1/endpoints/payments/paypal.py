import uuid
from typing import Any, List, Optional

import sqlalchemy
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from api import deps
from db.session import SessionLocal
from models.UserPayment import UserPayment
from schemas.Business import business_schema
from crud import crud_business, crud_user
import requests
import json
from utils.googleBucket import upload_business_profile_image

router = APIRouter()


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
    response = requests.post("https://api-m.paypal.com/v1/oauth2/token", data=data, headers=headers, auth=auth)

    # Parse the response
    response_json = response.json()
    if response.status_code == 200:
        # Access token retrieved successfully, return the token
        return response_json["access_token"]
    else:
        # Retrieving access token failed, return a 400 response with error description
        error_description = response.json().get("error_description",
                                                "Unknown error occurred while retrieving PayPal access token.")
        raise HTTPException(status_code=400, detail=error_description)


# Helper function to process PayPal payments
@router.get('/create-business-payment')
def process_paypal_payment():
    # Validate and process user information
    client_id = "AQAIjVIF5vcPBFdqi3szyM2O241eV4zde88Zxu3RoCo8syEZnHSDgBt5n-tXotYSLnb2ZtoTAlSasuWa"
    client_secret = "EG4qRVkXNHgawA55SrSoY7URH_RBbqR9lKzfjdX_p_OVji4E9DQq6zJoaWKcUnRdxq0lbM_Cm8MMgjN-"
    # Get the PayPal access token
    access_token = get_paypal_access_token(client_id, client_secret)
    # Set up the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(1.0),
                "currency": "USD"
            },
            "description": "Payment for business creation"
        }],
        "redirect_urls": {
            "return_url": "https://www.turklerden.com/payment-successful",
            "cancel_url": "https://www.turklerden.com/payment-cancelled"
        }
    }

    # Send the request
    response = requests.post("https://api-m.paypal.com/v1/payments/payment", data=json.dumps(payload),
                             headers=headers)

    # Parse the response
    response_json = response.json()
    if response.status_code == 201:
        # Payment created successfully, return the approval URL
        for link in response_json["links"]:
            if link["rel"] == "approval_url":
                return link["href"]
    else:
        # Payment creation failed, raise an exception
        raise Exception(response_json["message yes"])


@router.post('/execute-payment/{payment_id}/{payer_id}/{business_id}')
def execute_paypal_payment(payment_id: str, payer_id: str, business_id: int,
    db: Session = Depends(deps.get_db)
):
    client_id = "AY25dxn52cKNT6zBDO2IBqDMqSW5D6vqnr3UW3tnsMbOSvPgTjADOiHJmjrjR3rir9bopwUn6s6x_H1i"
    client_secret = "EC58RvUQz-OJW62_OHuS8JX2kIyJNa4eeiMimB6OIIS1Qbjmif3B1Tl7v2YaWr9lz2RHMLlJnFlBvxf2"

    # Get the PayPal access token
    access_token = get_paypal_access_token(client_id, client_secret)

    # Set up the request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Build the URL for the execute payment endpoint
    execute_payment_url = f"https://api-m.paypal.com/v1/payments/payment/{payment_id}/execute"

    # Create the payload for executing the payment with the payer_id
    payload = {
        "payer_id": payer_id
    }
    # Send the request to execute the payment
    response = requests.post(execute_payment_url, data=json.dumps(payload), headers=headers)
    # Parse the response
    response_json = response.json()
    if response.status_code == 200:
        business_activated = crud_business.business.activate(db, business_id)
        return {"business_activated_id": business_activated.id,
                "business_activated_name": business_activated.name}

    else:
        # Payment execution failed, raise an exception or handle accordingly
        raise HTTPException(status_code=500, detail=f"Payment execution failed: {response_json['message']}")
