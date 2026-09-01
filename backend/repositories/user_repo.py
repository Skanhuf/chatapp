from sqlalchemy import select, update, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User, Chat, ChatMember, Message


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def find_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_approved(self) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.status == "approved")
        )
        return list(result.scalars().all())

    async def get_pending(self) -> list[User]:
        result = await self.db.execute(
            select(User).where(User.status == "pending")
        )
        return list(result.scalars().all())

    async def approve(self, user_id: int) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(status="approved")
        )
        await self.db.commit()

    async def block(self, user_id: int) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(status="blocked")
        )
        await self.db.commit()

    async def search(self, query: str) -> list[User]:
        like_query = f"%{query}%"
        result = await self.db.execute(
            select(User).where(
                and_(User.username.like(like_query), User.status == "approved")
            )
        )
        return list(result.scalars().all())

    async def update_profile(self, user_id: int, email: str) -> None:
        await self.db.execute(
            update(User).where(User.id == user_id).values(email=email)
        )
        await self.db.commit()
