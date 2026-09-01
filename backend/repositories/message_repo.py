from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Message, User


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_by_chat_id(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        stmt = (
            select(Message, User)
            .join(User, Message.user_id == User.id)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        # Build messages with username from joined user
        messages = []
        for msg_row, user_row in rows:
            msg = Message(
                id=msg_row.id,
                chat_id=msg_row.chat_id,
                user_id=msg_row.user_id,
                content=msg_row.content,
                file_url=msg_row.file_url,
                created_at=msg_row.created_at,
            )
            msg.username = user_row.username if user_row else None
            messages.append(msg)
        # Reverse to get oldest first
        messages.reverse()
        return messages

    async def search(self, chat_id: int, query: str) -> list[Message]:
        like_query = f"%{query}%"
        stmt = (
            select(Message, User)
            .join(User, Message.user_id == User.id)
            .where(
                and_(Message.chat_id == chat_id, Message.content.like(like_query))
            )
            .order_by(Message.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        messages = []
        for msg_row, user_row in rows:
            msg = Message(
                id=msg_row.id,
                chat_id=msg_row.chat_id,
                user_id=msg_row.user_id,
                content=msg_row.content,
                file_url=msg_row.file_url,
                created_at=msg_row.created_at,
            )
            msg.username = user_row.username if user_row else None
            messages.append(msg)
        return messages
