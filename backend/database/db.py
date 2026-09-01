from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/chatapp")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        from models.models import Chat, ChatMember, Message, User  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for getting DB session."""
    async with async_session() as session:
        yield session
