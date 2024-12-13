from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

# from app.models.models import User
from app.db.db_connection import DB_SESSION
from app.settings import USER_SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-user")
def verify_token(token: str):
    try:
        # Convert the Secret object to a string
        secret_key = str(USER_SECRET_KEY)

        # Decode the token
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        sub: int = int(payload.get("sub"))
        user_role = payload.get("role")
    
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no sub found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user_role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Sorry, only admin can access this API"
            )
        return sub
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DB_SESSION):
    sub = verify_token(token)
    
    # Query the User model to get the current user
    # statement = select(User).where(User.user_id == sub)
    # user = session.exec(statement).first()

    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Token Provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sub
