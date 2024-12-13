from aiokafka import AIOKafkaConsumer
import asyncio
from app.protobuf import product_added_pb2  # Import the generated Protobuf module
from app.controllers.inventory_controller import add_new_product_in_inventory

async def consume_add_product_events(topic: str, bootstrap_servers: str):
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
                add_product_message = product_added_pb2.ProductAdded()
                add_product_message.ParseFromString(msg.value)

                print(f"Received event from Kafka: {add_product_message}")

                # Extract order details from the deserialized message
                product_id = int(add_product_message.product_id)
                quantity = int(add_product_message.quantity)
                brand = add_product_message.brand
                expiry = add_product_message.expiry
                price = add_product_message.price
 

                # Call a function to update the payment status in db for that specific order
                add_new_product_in_inventory(product_id, quantity, brand, price ,expiry)
            except Exception as e:
                print(f"Error processing Kafka message: {e}")

    except asyncio.CancelledError:
        print("Kafka consumer task was cancelled.")
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")
