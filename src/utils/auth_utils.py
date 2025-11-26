import datetime
from datetime import timedelta

import jwt
from dotenv import load_dotenv
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import exceptions
from pwdlib import PasswordHash

from src.constants.properties import SECRET_ACCESS_TOKEN, SECRET_ALGORITHM
from src.entities.db_model import User

load_dotenv()
password_hash = PasswordHash.recommended()

security = HTTPBearer()

def create_access_token(user: User):
    expire_time = datetime.datetime.now(datetime.UTC) + timedelta(days=30)
    token_data = {"sub": str(user.id), "exp": expire_time}
    access_token = jwt.encode(token_data, SECRET_ACCESS_TOKEN, algorithm=SECRET_ALGORITHM)
    return access_token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_ACCESS_TOKEN, algorithms=[SECRET_ALGORITHM])
        return payload
    except exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except (exceptions.DecodeError, exceptions.InvalidSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = User.get_or_none(User.id == user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user