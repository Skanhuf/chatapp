
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from repositories.user_repo import UserRepository
from schemas.auth import LoginRequest, LoginResponse, ProfileUpdateRequest, RegisterRequest, UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_id_from_cookie(user_id: str | None = Cookie(None)) -> int:
    """Extract user ID from cookie."""
    if user_id is None or user_id == "":
        raise HTTPException(status_code=401, detail="unauthorized")
    return int(user_id)


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    try:
        user = await auth_service.register(req.username, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        raise HTTPException(status_code=401, detail=str(e))

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
        raise HTTPException(status_code=404, detail=str(e))

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
        raise HTTPException(status_code=400, detail=str(e))

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
