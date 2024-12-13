from aiokafka import AIOKafkaConsumer
import asyncio
from app.protobuf import payment_status_pb2  # Import the generated Protobuf module
from app.controllers.order_crud import update_payment_status

async def consume_payment_status_events(topic: str, bootstrap_servers: str):
    """
    Kafka consumer function that continuously listens to payment status events in the given topic using Protobuf deserialization.
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
                # Deserialize the message using Protobuf
                payment_status_message = payment_status_pb2.PaymentStatus()
                payment_status_message.ParseFromString(msg.value)

                print(f"Received event from Kafka: {payment_status_message}")

                # Extract order details from the deserialized message
                order_id = int(payment_status_message.order_id)
                user_id = int(payment_status_message.user_id)
                payment_status = payment_status_message.payment_status

                # Call a function to update the payment status in db for that specific order
                await update_payment_status(order_id, payment_status)
            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")
