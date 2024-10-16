from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from typing import Annotated
from app.db.db_connection import DB_SESSION
from fastapi.security import OAuth2PasswordBearer

from app.settings import USER_SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-user")
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
    

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DB_SESSION):
    email = verify_token(token)
    
    # Query the User model to get the current user
    # statement = select(User).where(User.email == email)
    # user = session.exec(statement).first()

    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="The users whose token is provided doesn't exist in the db",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # return user
