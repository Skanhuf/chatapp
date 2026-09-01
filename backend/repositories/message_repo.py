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
            select(Message)
            .join(User, Message.user_id == User.id)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = result.scalars().all()
        # Reverse to get oldest first
        rows.reverse()
        return rows

    async def search(self, chat_id: int, query: str) -> list[Message]:
        like_query = f"%{query}%"
        result = await self.db.execute(
            select(Message)
            .join(User, Message.user_id == User.id)
            .where(
                and_(Message.chat_id == chat_id, Message.content.like(like_query))
            )
            .order_by(Message.created_at.desc())
        )
        return list(result.scalars().all())
