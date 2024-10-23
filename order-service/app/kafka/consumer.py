from aiokafka import AIOKafkaConsumer
import asyncio
import json
from app.controllers.order_crud import update_payment_status

async def consume_payment_status_events(topic: str, bootstrap_servers: str):
    """
    Kafka consumer function that continuously listens to payment status events in the given topic.
    """
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=[bootstrap_servers],
        group_id="payment-events-consumer-group",
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    await consumer.start()
    print("Kafka consumer started and actively listening...")
    try:
        async for msg in consumer:
            try:
                message = json.loads(msg.value.decode('utf-8'))
                print(f"Received event from Kafka: {message}")

                # Extract order details from the message
                order_id = message.get("order_id")
                user_id = message.get("user_id")
                payment_status = message.get("payment_status")

                # Call a function to update the payment status in db for that specific order
                await update_payment_status(order_id, payment_status)
            except json.JSONDecodeError:
                print("Failed to decode Kafka message as JSON.")
            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")