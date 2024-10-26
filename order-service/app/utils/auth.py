from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, Depends, status

from app.db.db_connection import DB_SESSION
from app.settings import USER_SECRET_KEY, ALGORITHM



# ============================== DECODE TOKEN ================================
def decode_jwt_token(token: str):
    try:
        # Decode the token using the same secret key and algorithm
        secret_key = str(USER_SECRET_KEY)        
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        
        return payload
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    

# ============================== GET user_id ================================
def get_user_id_from_token(token: str):
    # Decode the JWT token
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = decode_jwt_token(token)
    user_id = int(payload.get("sub"))
    # user_role = payload.get("role")
    # if user_role != "user":
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Sorry, only users can place order."
    #     )

    return user_id