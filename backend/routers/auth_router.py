from fastapi import APIRouter, HTTPException, Depends, Response
from typing import Optional

from schemas.auth import (
    RegisterRequest, LoginRequest, ProfileUpdateRequest,
    UserResponse, LoginResponse
)
from services.auth_service import AuthService
from repositories.user_repo import UserRepository
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_id_from_cookie(user_id: Optional[str] = Depends(lambda x: x)) -> int:
    """Extract user ID from cookie."""
    raise HTTPException(status_code=401, detail="unauthorized")


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        user = await auth_service.register(req.username, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "id": user.id,
        "username": user.username,
        "status": "pending",
        "message": "Registration successful. Please wait for admin approval."
    }


@router.post("/login")
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        user = await auth_service.login(req.username, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    response.set_cookie(
        key="userId",
        value=str(user.id),
        max_age=86400,
        httponly=True,
        samesite="lax"
    )

    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email
    )


@router.get("/me")
async def get_me(user_id: int = Depends(get_user_id_from_cookie), db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        user = await auth_service.get_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        status=user.status
    )


@router.put("/profile")
async def update_profile(
    req: ProfileUpdateRequest,
    user_id: int = Depends(get_user_id_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        await auth_service.update_profile(user_id, req.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"message": "Profile updated"}


@router.get("/search")
async def search_users(
    q: str = "",
    user_id: int = Depends(get_user_id_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    users = await auth_service.search_users(q)
    return [
        UserResponse(
            id=u.id, username=u.username, email=u.email, status=u.status
        )
        for u in users
    ]
