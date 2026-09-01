from fastapi import APIRouter, HTTPException, Depends, Request

from schemas.auth import (
    CreateChatRequest, CreateDirectChatRequest,
    AddMemberRequest, ChatResponse, ChatMemberResponse
)
from services.chat_service import ChatService
from services.message_service import MessageService
from repositories.user_repo import UserRepository
from repositories.chat_repo import ChatRepository
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/chats", tags=["chats"])


async def get_user_id(request: Request) -> int:
    """Get user ID from cookie."""
    user_id = request.cookies.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    return int(user_id)


@router.get("")
async def get_chats(
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    chats = await chat_service.get_chats(user_id)
    return [
        ChatResponse(
            id=c.id, name=c.name, type=c.type,
            created_by=c.created_by, created_at=c.created_at
        )
        for c in chats
    ]


@router.post("", status_code=201)
async def create_chat(
    req: CreateChatRequest,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    try:
        chat = await chat_service.create_chat(req.name, user_id, req.member_ids)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ChatResponse(
        id=chat.id, name=chat.name, type=chat.type,
        created_by=chat.created_by, created_at=chat.created_at
    )


@router.post("/direct", status_code=201)
async def create_direct_chat(
    req: CreateDirectChatRequest,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    try:
        chat_id = await chat_service.create_direct_chat(user_id, req.participant_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"chat_id": chat_id}


@router.get("/{chat_id}/members")
async def get_chat_members(
    chat_id: int,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    members = await chat_service.get_members(chat_id)
    return [
        ChatMemberResponse(
            id=m.id, username=m.username, email=m.email,
            status=m.status, created_at=m.created_at
        )
        for m in members
    ]


@router.post("/{chat_id}/members")
async def add_member(
    chat_id: int,
    req: AddMemberRequest,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    try:
        await chat_service.add_member(chat_id, req.user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Member added"}


@router.delete("/{chat_id}/members/{member_id}")
async def remove_member(
    chat_id: int,
    member_id: int,
    request: Request,
    auth_user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    if auth_user_id == member_id:
        raise HTTPException(status_code=400, detail="cannot leave your own chat")

    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    try:
        await chat_service.remove_member(chat_id, member_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Member removed"}


@router.post("/{chat_id}/leave")
async def leave_chat(
    chat_id: int,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo, user_repo)

    try:
        await chat_service.remove_member(chat_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Left chat"}


# Admin routes
@router.get("/admin/users")
async def get_pending_users(
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    users = await user_repo.get_pending()
    return [
        {"id": u.id, "username": u.username, "email": u.email, "status": u.status}
        for u in users
    ]


@router.put("/admin/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    try:
        await user_repo.approve(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User approved"}


@router.put("/admin/users/{user_id}/block")
async def block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    try:
        await user_repo.block(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User blocked"}
