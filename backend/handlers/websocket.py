import json

from fastapi import WebSocket

from models.models import Message
from services.chat_service import ChatService
from services.message_service import MessageService


class WSClient:
    def __init__(self, websocket: WebSocket, user_id: int):
        self.websocket = websocket
        self.user_id = user_id
        self.send_queue: list[bytes] = []


class WSHub:
    def __init__(self):
        self.clients: dict[int, WSClient] = {}
        self.broadcast_queue: list[tuple[int, bytes]] = []

    def register(self, client: WSClient):
        self.clients[client.user_id] = client

    def unregister(self, user_id: int):
        if user_id in self.clients:
            del self.clients[user_id]

    def add_broadcast(self, chat_id: int, data: bytes):
        self.broadcast_queue.append((chat_id, data))

    async def process_broadcasts(self):
        """Process queued broadcasts and send to relevant clients."""
        while self.broadcast_queue:
            chat_id, data = self.broadcast_queue.pop(0)
            # Broadcast to all connected clients (frontend will filter by chat_id)
            for client in list(self.clients.values()):
                try:
                    await client.websocket.send_bytes(data)
                except Exception:
                    self.unregister(client.user_id)


class WebSocketHandler:
    def __init__(self, chat_service: ChatService, message_service: MessageService, hub: WSHub):
        self.chat_service = chat_service
        self.message_service = message_service
        self.hub = hub

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        client = WSClient(websocket, user_id)
        self.hub.register(client)

    async def disconnect(self, user_id: int):
        self.hub.unregister(user_id)

    async def handle_message(self, user_id: int, chat_id: int, content: str):
        msg = Message(
            id=0, chat_id=chat_id, user_id=user_id,
            content=content, file_url=None,
            created_at=None, username=None
        )

        await self.message_service.send_message(msg)

        # Get username
        user = await self.chat_service.get_user_by_id(user_id)
        if user:
            msg.username = user.username

        # Serialize and broadcast
        data = json.dumps({
            "id": msg.id,
            "chat_id": msg.chat_id,
            "user_id": msg.user_id,
            "content": msg.content,
            "file_url": msg.file_url,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "username": msg.username
        })
        self.hub.add_broadcast(chat_id, data.encode("utf-8"))
