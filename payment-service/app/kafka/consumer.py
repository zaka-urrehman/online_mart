from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.controllers.payment_crud import process_stripe_payment

async def consume_order_events(topic: str, bootstrap_servers: str):
    """
    Kafka consumer function that continuously listens to order events in the given topic.
    """
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=[bootstrap_servers],
        group_id="order-events-consumer-group",
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    await consumer.start()
    print("Kafka consumer started and actively listening...")
    try:
        async for msg in consumer:
            try:
                message = json.loads(msg.value.decode('utf-8'))
                print(f"Received order event from Kafka: {message}")

                # Extract order details from the message
                order_id = message.get("order_id")
                user_id = message.get("user_id")
                net_amount = message.get("net_amount")

                # Call the Stripe payment function for each order
                await process_stripe_payment(order_id, user_id, net_amount)

            except json.JSONDecodeError:
                print("Failed to decode Kafka message as JSON.")
            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")
