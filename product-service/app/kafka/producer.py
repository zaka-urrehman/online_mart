from typing import Annotated
from aiokafka import AIOKafkaProducer  
from fastapi import Depends


# ========================================= Dependency Injection ========================================================
async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    print("Producer Starting....!")
    try:
        yield producer
    finally:
        print("Producer is stopped....!")
        await producer.stop()


# =================================================================================================

KAFKA_PRODUCER = Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]