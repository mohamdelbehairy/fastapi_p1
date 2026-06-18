from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from math import ceil

from app.core.security import get_current_user
from app.models.user import User
from app.database import get_session
from app.schemas.edit_user_data import EditUserData


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("")
async def get_all_users(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=20, ge=1, le=100),
):
    offset = (page - 1) * limit
    
    total = session.exec(
        select(func.count())
        .select_from(User)
        .where(User.id != current_user.id)
    ).one()

    all_users = session.exec(
        select(User)
        .where(User.id != current_user.id)
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "page": page,
        "limit": limit,
        "total_users": total,
        "data": [
            user.model_dump(exclude={"password"})
            for user in all_users
        ]
    }

@router.get("/me")
async def get_user_data(
        current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "fullName": current_user.fullName,
        "email": current_user.email,
        "age": current_user.age,
    }

@router.put("/me")
async def edit_user_data(
        data: EditUserData,
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
):
    if data.email is not None and data.email != current_user.email:
        existing_user = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        current_user.email = data.email or ""


    if data.fullName is not None:
        current_user.fullName = data.fullName

    if data.email is not None:
        current_user.email = data.email

    if data.age is not None:
        current_user.age = data.age

    session.commit()
    session.refresh(current_user)

    return {
        "message": "user updated successfully",
    }

@router.delete("/me")
async def delete_user(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session),
):
    session.delete(current_user)
    session.commit()
    return {
        "message": "user deleted successfully",
    }