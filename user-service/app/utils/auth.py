from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from passlib.context import CryptContext

from app.models.user_models import User
from app.settings import USER_SECRET_KEY, ALGORITHM

# Create a password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by the user."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(user: User, expire_delta: timedelta):
    # Set the expiration time for the token
    expire = datetime.utcnow() + expire_delta
    print("expiry: " , expire)

    # Payload to encode in the token
    payload = {
        "sub": user.email,
        "phone": user.phone,  # 'sub' claim (subject) typically stores the username or user ID
        "exp": expire
    }

    secret_key = str(USER_SECRET_KEY)   
    print("payload: " , payload)
    print("user secret: " , secret_key)
    print(f"user secret (length {len(secret_key)}): '{secret_key}'")
    print("algorithm: " , ALGORITHM)
    # Generate the token using jose's jwt.encode
    token = jwt.encode(payload, secret_key, algorithm=ALGORITHM)

    return token


def verify_token(token: str):
    try:
        # Convert the Secret object to a string
        secret_key = str(USER_SECRET_KEY)

        # Decode the token
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no email found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )