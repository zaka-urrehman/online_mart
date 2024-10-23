import stripe
import os
import logging
from fastapi import APIRouter, Request, HTTPException

from app.settings import STRIPE_API_KEY, WEBHOOK_SECRET, KAFKA_PAYMENT_STATUS_TOPIC
from app.controllers.payment_crud import send_payment_status_to_kafka  # Import the Kafka producer

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_API_KEY

router = APIRouter()

@router.post("/stripe-webhook", status_code=200)
async def stripe_webhook(request: Request):
    """
    Stripe webhook to handle events like payment confirmation, failures, etc.
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    # Verify the webhook signature using Stripe's SDK
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    print("event:" , event)

    # Handle different event types
    event_type = event['type']
    event_data = event['data']['object']

    if event_type == 'payment_intent.succeeded':
        print("in succeeded block here")
        # Payment succeeded
        payment_intent_id = event_data['id']
        user_id = event_data.get('metadata', {}).get('user_id')
        order_id = event_data.get('metadata', {}).get('order_id')
        net_amount = event_data['amount_received'] / 100  # Convert from cents to currency unit
        print("user_id: ", user_id)
        print("order_id: ", order_id)
        logger.info(f"Payment succeeded for PaymentIntent ID: {payment_intent_id}")

        # Call the Kafka producer to send payment status to Kafka
        if user_id and order_id:
            payment_status = "paid"
            await send_payment_status_to_kafka(
                topic=KAFKA_PAYMENT_STATUS_TOPIC,
                order_id=int(order_id),
                user_id=int(user_id),
                payment_status=payment_status
            )
            logger.info(f"Sent payment status to Kafka for Order ID: {order_id}, User ID: {user_id}")

    elif event_type == 'payment_intent.payment_failed':
        # Payment failed
        logger.info(f"Payment failed for PaymentIntent ID: {event_data['id']}")
        # Handle payment failure (e.g., notify user)

    else:
        # Handle other events if needed
        logger.info(f"Unhandled event type: {event_type}")

    return {"message": "Webhook received successfully"}
