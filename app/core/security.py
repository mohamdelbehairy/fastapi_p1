from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from starlette import status

from app.core.config import SECRET_KEY, ALGORITHM
from app.database import get_session
from app.models.user import User

def create_token(data: dict, expire_delta: timedelta, token_type: str):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expire_delta

    to_encode.update({
        "exp": int(expire.timestamp()),
        "type": token_type
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def create_access_token(data: dict):
   return create_token(
       data=data,
       expire_delta=timedelta(minutes=30),
       token_type='access'
   )

def create_refresh_token(data: dict):
    return create_token(
        data=data,
        expire_delta=timedelta(days=7),
        token_type='refresh'
    )

security = HTTPBearer()
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
):
    token = credentials.credentials

    try :
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    return user

def refresh_token_logic(
        refresh_token: str,
        session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid refresh token"
        )

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    new_access_token = create_access_token({
        "sub": user_id,
        "type": "access"
    })

    return {
        "access_token": new_access_token,
        "token_type": "access",
    }