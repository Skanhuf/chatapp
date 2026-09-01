from fastapi import APIRouter, HTTPException, Depends, Request

from schemas.auth import SendMessageRequest, MessageResponse
from services.message_service import MessageService
from repositories.message_repo import MessageRepository
from repositories.chat_repo import ChatRepository
from models.models import Message
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/messages", tags=["messages"])


async def get_user_id(request: Request) -> int:
    """Get user ID from cookie."""
    user_id = request.cookies.get("userId")
    if not user_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    return int(user_id)


@router.get("/{chat_id}")
async def get_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    message_repo = MessageRepository(db)
    chat_repo = ChatRepository(db)
    message_service = MessageService(message_repo, chat_repo)

    msg_tuples = await message_service.get_messages(chat_id, limit, offset)
    return [
        MessageResponse(
            id=msg.id, chat_id=msg.chat_id, user_id=msg.user_id,
            content=msg.content, file_url=msg.file_url,
            created_at=msg.created_at, username=username
        )
        for msg, username in msg_tuples
    ]


@router.post("", status_code=201)
async def send_message(
    req: SendMessageRequest,
    request: Request,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    message_repo = MessageRepository(db)
    chat_repo = ChatRepository(db)
    message_service = MessageService(message_repo, chat_repo)

    msg = Message(
        chat_id=req.chat_id, user_id=user_id,
        content=req.content,
    )

    try:
        saved_msg = await message_service.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return MessageResponse(
        id=saved_msg.id, chat_id=saved_msg.chat_id, user_id=saved_msg.user_id,
        content=saved_msg.content, file_url=saved_msg.file_url,
        created_at=saved_msg.created_at, username=None
    )
