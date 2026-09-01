import json

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from handlers.websocket import WebSocketHandler, WSHub
from repositories.chat_repo import ChatRepository
from repositories.message_repo import MessageRepository
from repositories.user_repo import UserRepository
from services.chat_service import ChatService
from services.message_service import MessageService

router = APIRouter(tags=["websocket"])


# Hub is shared across all WebSocket connections
hub = WSHub()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Get user ID from query param
    user_id_str = websocket.query_params.get("userId")
    if not user_id_str:
        await websocket.close(code=4001, reason="Missing userId")
        return

    try:
        user_id = int(user_id_str)
    except ValueError:
        await websocket.close(code=4001, reason="Invalid userId")
        return

    # Initialize services
    user_repo = UserRepository(db)
    chat_repo = ChatRepository(db)
    message_repo = MessageRepository(db)

    chat_service = ChatService(chat_repo, user_repo)
    message_service = MessageService(message_repo, chat_repo)

    ws_handler = WebSocketHandler(chat_service, message_service, hub)

    await ws_handler.connect(websocket, user_id)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            msg_type = data.get("type")
            if msg_type == "message":
                chat_id = data.get("chat_id")
                content = data.get("content")
                if chat_id and content:
                    await ws_handler.handle_message(user_id, chat_id, content)
    except WebSocketDisconnect:
        await ws_handler.disconnect(user_id)
