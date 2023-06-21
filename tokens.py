from datetime import datetime, timedelta

from fastapi import HTTPException

from jose import JWTError, jwt

from config import settings

def create_access_token(data: dict, expire_delta):
    
    to_encode = data.copy()
    # expire = datetime.utcnow() + timedelta(minutes=15)
    expire = datetime.utcnow() + expire_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt

def verify_tokens(token: str):
    credentials_exception = HTTPException(
        status_code=401,detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        email: str = payload.get("sub")
        return email
        # if email is None:
        #     raise credentials_exception
    except JWTError:
        raise credentials_exception

