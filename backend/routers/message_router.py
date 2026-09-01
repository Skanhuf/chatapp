from fastapi import APIRouter, HTTPException, Depends

from schemas.auth import SendMessageRequest, MessageResponse
from services.message_service import MessageService
from repositories.message_repo import MessageRepository
from repositories.chat_repo import ChatRepository
from models.models import Message
from database.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/messages", tags=["messages"])


async def get_user_id(request):
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

    messages = await message_service.get_messages(chat_id, limit, offset)
    return [
        MessageResponse(
            id=m.id, chat_id=m.chat_id, user_id=m.user_id,
            content=m.content, file_url=m.file_url,
            created_at=m.created_at, username=m.username
        )
        for m in messages
    ]


@router.post("", status_code=201)
async def send_message(
    req: SendMessageRequest,
    user_id: int = Depends(get_user_id),
    db: AsyncSession = Depends(get_db)
):
    message_repo = MessageRepository(db)
    chat_repo = ChatRepository(db)
    message_service = MessageService(message_repo, chat_repo)

    msg = Message(
        id=0, chat_id=req.chat_id, user_id=user_id,
        content=req.content, file_url=None,
        created_at=None, username=None
    )

    try:
        saved_msg = await message_service.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return MessageResponse(
        id=saved_msg.id, chat_id=saved_msg.chat_id, user_id=saved_msg.user_id,
        content=saved_msg.content, file_url=saved_msg.file_url,
        created_at=saved_msg.created_at, username=saved_msg.username
    )
