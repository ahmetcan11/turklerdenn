import stripe
import stripe.error as stripe_errors
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from stripe.error import StripeError


YOUR_DOMAIN_LOCAL = 'http://localhost:3000'
YOUR_DOMAIN_PROD = 'https://www.turklerden.com'


def create_stripe_customer(email):
    customer = stripe.Customer.create(email=email)
    return customer.id


def set_active_card_for_customer(customer_id, payment_method_id):
    customer = stripe.Customer.modify(
        customer_id,
        invoice_settings={
            'default_payment_method': payment_method_id
        }
    )
    return customer


def create_payment_token(card_number, exp_month, exp_year, cvc):
    token = stripe.Token.create(
        card={
            'number': card_number,
            'exp_month': int(exp_month),
            'exp_year': int(exp_year),
            'cvc': cvc
        }
    )
    return token.id


def add_payment_method(customer_id, payment_token_id):
    # Create the payment method
    payment_method = stripe.PaymentMethod.create(
        type="card",
        card={
            "token": payment_token_id
        }
    )

    # Attach the payment method to the customer
    payment_method = stripe.PaymentMethod.attach(
        payment_method.get("id"),
        customer=customer_id
    )

    # Set the payment method as the default for the customer
    set_active_card_for_customer(customer_id=customer_id, payment_method_id=payment_method.get("id"))

    return payment_method.get("id")


def charge_for_business_account(customer_id, payment_method_id, amount=100, currency="usd"):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            description="Business user account creation fee",
            payment_method_types=["card"],
            payment_method=payment_method_id
        )
        payment_intent.confirm()

        return payment_intent

    except stripe_errors.CardError as e:
        # Handle specific card errors
        error_message = e.user_message or str(e)
        raise Exception(f"Card Error: {error_message}")
    except stripe_errors.StripeError as e:
        # Handle other Stripe API errors
        error_message = e.user_message or str(e)
        raise Exception(f"Stripe Error: {error_message}")
    except Exception as e:
        # Handle other generic errors
        error_message = str(e)
        raise Exception(f"Error: {error_message}")


def create_session_business(price_id: str, business_id: str):
    try:
        custom_data = {
            'business_id': business_id,
        }
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN_PROD + '/payment-successful',
            cancel_url=YOUR_DOMAIN_PROD + '/payment-cancel',
            metadata=custom_data,
        )

        return checkout_session

    except StripeError as e:
        # Return a 400 Bad Request status code for Stripe errors
        raise HTTPException(status_code=400, detail="Stripe Error: " + str(e))

    except Exception as e:
        # Return a 500 Internal Server Error status code for other exceptions
        raise HTTPException(status_code=500, detail="Internal Server Error")


def get_session_info(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except Exception as e:
        return {"Error during retrieving payment info": e}

