from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from sqlmodel import select
from typing import Annotated
 
from app.models.user_models import UserAuth, User  # Assuming UserAuth is a Pydantic model and User is the SQLModel model
from app.db.db_connection import DB_SESSION
from app.settings import USER_SECRET_KEY, ALGORITHM, USER_TOKEN_EXPIRE_TIME
from app.utils.auth import verify_password, generate_token, verify_token  # Import your verify_password function


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-user")

def login_user(user_details: UserAuth, session: DB_SESSION):
    # Query the User table using the email field
    statement = select(User).where(User.email == user_details.email)
    user = session.exec(statement).first()

    if not user or not verify_password(user_details.password, user.password):  # Use your verify_password function
        return {"error": "Invalid credentials"}

    # If authentication is successful, generate a token
    access_token_expires = timedelta(days=USER_TOKEN_EXPIRE_TIME)
    access_token = generate_token(user, expire_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}



def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DB_SESSION):
    sub = verify_token(token)
    
    # Query the User model to get the current user
    statement = select(User).where(User.user_id == sub)
    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The users whose token is provided doesn't exist in the db",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
