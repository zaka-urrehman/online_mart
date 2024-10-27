from aiokafka import AIOKafkaConsumer
import asyncio
from app.protobuf import order_pb2  # Import the generated Protobuf module
from app.controllers.payment_crud import process_stripe_payment

async def consume_order_events(topic: str, bootstrap_servers: str):
    """
    Kafka consumer function that continuously listens to order events in the given topic using Protobuf deserialization.
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
                # Deserialize the message using Protobuf
                order_message = order_pb2.Order()
                order_message.ParseFromString(msg.value)

                print(f"Received order event from Kafka: {order_message}")

                # Extract order details from the deserialized message
                order_id = int(order_message.order_id)
                user_id = int(order_message.user_id)
                net_amount = float(order_message.net_amount)

                # Call the Stripe payment function for each order
                await process_stripe_payment(order_id, user_id, net_amount)

            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")
