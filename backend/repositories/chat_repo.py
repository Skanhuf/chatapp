from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Chat, ChatMember, User


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, chat: Chat) -> Chat:
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_by_user_id(self, user_id: int) -> list[Chat]:
        result = await self.db.execute(
            select(Chat).join(ChatMember).where(ChatMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_members(self, chat_id: int) -> list[User]:
        result = await self.db.execute(
            select(User).join(ChatMember).where(ChatMember.chat_id == chat_id)
        )
        return list(result.scalars().all())

    async def add_member(self, chat_id: int, user_id: int, role: str) -> None:
        await self.db.execute(
            insert(ChatMember).values(
                chat_id=chat_id, user_id=user_id, role=role
            )
        )
        await self.db.commit()

    async def remove_member(self, chat_id: int, user_id: int) -> None:
        await self.db.execute(
            delete(ChatMember).where(
                and_(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id)
            )
        )
        await self.db.commit()

    async def create_direct_chat(self, user1_id: int, user2_id: int) -> int:
        chat = Chat(name="Direct", chat_type="direct", created_by=user1_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)

        await self.add_member(chat.id, user1_id, "admin")
        await self.add_member(chat.id, user2_id, "admin")

        return chat.id
