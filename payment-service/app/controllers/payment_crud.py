import stripe
import asyncio
import logging
import json

from aiokafka import AIOKafkaProducer

from app.settings import STRIPE_API_KEY
from app.kafka.producer import KAFKA_PRODUCER

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe with the API key
stripe.api_key = STRIPE_API_KEY


# ==================================== PROCESS PAYMENT THROUGH STRIPE =====================================

async def process_stripe_payment(order_id: int, user_id: int, net_amount: float):
    """
    Function to process payment through Stripe using a test token.
    """
    logger.info(f"Initiating payment for Order ID: {order_id}, User ID: {user_id}, Amount: {net_amount}")

    try:
        # Convert the amount to cents for Stripe (assuming USD)
        amount_in_cents = int(net_amount * 100)

        # Step 1: Create a PaymentIntent and confirm it using a test token
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='usd',
            payment_method="pm_card_visa",  # Using Stripe's predefined test token
            confirm=True,
            description=f"Order {order_id} for User {user_id}",
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"  # Disable redirect-based methods
            },
            metadata={
            "user_id": user_id,
            "order_id": order_id
            }
        )
        logger.info(f"Stripe PaymentIntent created and confirmed for Order ID: {order_id}, Intent ID: {intent['id']}")

        # Check if the payment is successful
        if intent['status'] == 'succeeded':
            payment_response = {
                "status": "success",
                "order_id": order_id,
                "user_id": user_id,
                "net_amount": net_amount,
                "stripe_payment_id": intent['id'],
                "message": "Payment processed successfully."
            }
            logger.info(f"Payment successful for Order ID: {order_id}, Amount: {net_amount}")
        else:
            payment_response = {
                "status": "pending",
                "order_id": order_id,
                "user_id": user_id,
                "net_amount": net_amount,
                "stripe_payment_id": intent['id'],
                "message": f"Payment status is {intent['status']}."
            }
            logger.info(f"Payment not yet successful for Order ID: {order_id}. Status: {intent['status']}")

        return payment_response

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error occurred for Order ID: {order_id}: {str(e)}")
        return {
            "status": "failed",
            "order_id": order_id,
            "user_id": user_id,
            "net_amount": net_amount,
            "message": f"Payment failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"An error occurred for Order ID: {order_id}: {str(e)}")
        return {
            "status": "failed",
            "order_id": order_id,
            "user_id": user_id,
            "net_amount": net_amount,
            "message": f"Payment failed: {str(e)}"
        }



    


# ============================== SEND PAYMENT STATUS TO KAFKA TOPIC ==============================
async def send_payment_status_to_kafka(topic: str, order_id: int, user_id: int, payment_status: str, bootstrap_servers: str = 'broker:19092'):
    """
    Send payment status to Kafka topic.

    Args:
        topic (str): Kafka topic name.
        order_id (int): The ID of the order.
        user_id (int): The ID of the user.
        payment_status (str): The status of the payment (e.g., 'paid').
        bootstrap_servers (str): Kafka bootstrap server.
    """
    # Initialize the Kafka producer
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    # Start the producer
    await producer.start()

    try:
        # Create the message payload
        message = {
            "order_id": order_id,
            "user_id": user_id,
            "payment_status": payment_status
        }

        # Send the message to the specified Kafka topic
        await producer.send_and_wait(topic, message)

        print(f"Payment status for Order ID {order_id} sent to Kafka topic '{topic}'")
    except Exception as e:
        print(f"Failed to send payment status to Kafka: {str(e)}")
    finally:
        # Stop the producer after sending the message
        await producer.stop()

    
    


