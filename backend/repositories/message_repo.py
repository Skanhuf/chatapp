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
        result = await self.db.execute(
            select(
                Message.id, Message.chat_id, Message.user_id,
                Message.content, Message.file_url, Message.created_at,
                User.username
            )
            .join(User, Message.user_id == User.id)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = result.all()
        messages = [
            Message(
                id=row.id, chat_id=row.chat_id, user_id=row.user_id,
                content=row.content, file_url=row.file_url,
                created_at=row.created_at, username=row.username
            )
            for row in rows
        ]
        # Reverse to get oldest first
        messages.reverse()
        return messages

    async def search(self, chat_id: int, query: str) -> list[Message]:
        like_query = f"%{query}%"
        result = await self.db.execute(
            select(
                Message.id, Message.chat_id, Message.user_id,
                Message.content, Message.file_url, Message.created_at,
                User.username
            )
            .join(User, Message.user_id == User.id)
            .where(
                and_(Message.chat_id == chat_id, Message.content.like(like_query))
            )
            .order_by(Message.created_at.desc())
        )
        rows = result.all()
        return [
            Message(
                id=row.id, chat_id=row.chat_id, user_id=row.user_id,
                content=row.content, file_url=row.file_url,
                created_at=row.created_at, username=row.username
            )
            for row in rows
        ]
