from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pwdlib import PasswordHash

from app.models.user import User
from app.schemas.create_account import CreateAccount
from app.schemas.login import Login
from app.database import get_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    refresh_token_logic
)
from app.schemas.refresh_token import RefreshTokenLogic


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

password_hash = PasswordHash.recommended()

@router.post("/create_account")
async def create_account(data: CreateAccount, session: Session = Depends(get_session)):
    exiting_user = session.exec(select(User).where(User.email == data.email)).first()

    if exiting_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered")


    new_data = data.model_dump()
    new_data["password"] = password_hash.hash(data.password)

    new_user = User(**new_data)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    access_token = create_access_token(
        {
            "sub": new_user.id
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": new_user.id
        }
    )

    return {
        "message": "Account created successfully",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    }

@router.post("/login")
async def login(data: Login, session: Session = Depends(get_session)):
    exiting_user = session.exec(select(User).where(User.email == data.email)).first()
    if not exiting_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    if not password_hash.verify(data.password, exiting_user.password):
        raise HTTPException(
            status_code=404,
            detail="Incorrect password"
        )

    access_token = create_access_token(
        {
            "sub": exiting_user.id
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": exiting_user.id
        }
    )

    return {
        "message": "Login successfully",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    }

@router.post("/refresh_token")
async def refresh(
        token: RefreshTokenLogic,
        session: Session = Depends(get_session)):
   return refresh_token_logic(token.refresh_token, session)




