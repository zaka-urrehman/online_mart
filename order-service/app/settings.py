from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config() 

DATABASE_URL = config("DATABASE_URL", cast = Secret) 
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast = Secret)

USER_SECRET_KEY = config("USER_SECRET_KEY", cast = Secret)
ADMIN_SECRET_KEY = config("ADMIN_SECRET_KEY", cast = Secret)
ADMIN_TOKEN_EXPIRY_TIME = config("ADMIN_TOKEN_EXPIRY_TIME", cast = int)
USER_TOKEN_EXPIRE_TIME = config("USER_TOKEN_EXPIRE_TIME", cast = int)
ALGORITHM = config("ALGORITHM", cast = str)

KAFKA_NOTIFICATION_TOPIC = config("KAFKA_NOTIFICATION_TOPIC", cast = str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast = str)
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast = str)
KAFKA_PAYMENT_STATUS_TOPIC = config("KAFKA_PAYMENT_STATUS_TOPIC", cast = str)