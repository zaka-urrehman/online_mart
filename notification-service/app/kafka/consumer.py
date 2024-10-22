import json 

from aiokafka import AIOKafkaConsumer
from app.models.email_model import NotificationBase
from app.controllers.notification_crud import send_email_notification



async def consume_notification_events(topic: str, bootstrap_servers: str):
    """
    Generic Kafka consumer function that consumes messages from the given topic.
    Args:
        topic (str): The Kafka topic to listen to.
        bootstrap_servers (str): The Kafka bootstrap server.
    """
    # Step 1: Create a Kafka consumer instance
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="notification-consumer-group",
        auto_offset_reset='earliest'
    )

     # Step 2: Start the consumer
    await consumer.start()
    print(f"Started consuming from topic: {topic}")
    
    try:
        # Step 3: Continuously listen for messages from Kafka 
        async for msg in consumer:
            try:
                # Step 4: Deserialize the  message from JSON
                notification_data = json.loads(msg.value.decode('utf-8'))
                email = notification_data.get('email')
                message = notification_data.get('message')
                event_type = notification_data.get('event_type')

                # Step 5: Prepare the NotificationBase object for sending email
                notification = NotificationBase(
                    email=email,
                    title=event_type,  # Use event type as the title
                    message=message
                )

                # Step 6: Send the email notification
                response = send_email_notification(notification)
                print(f"Message sent: {response}")

            except Exception as e:
                print(f"Failed to process message: {e}") 

    except Exception as e:
        print(f"Error consuming from topic '{topic}': {e}")

    finally:
        # Step 7: Stop the consumer gracefully
        await consumer.stop()
        print(f"Stopped consuming from topic: {topic}")