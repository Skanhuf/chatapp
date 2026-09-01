import os
import tempfile

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app

# Import Base from models to avoid importing database.db (which creates PG engine)
from models.models import Base, Chat, ChatMember, Message, User  # noqa: F401

# Use a temp file for SQLite so all connections share the same DB
_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "chatapp_test.db")
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{_TEST_DB_PATH}"

_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Create and drop tables for each test to ensure isolation."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session(setup_db):
    """Provide a session with rollback (per-test, new connection)."""
    async with _test_engine.connect() as conn:
        await conn.begin()
        s = async_sessionmaker(conn, class_=AsyncSession, expire_on_commit=False)()
        try:
            yield s
            await s.rollback()
        finally:
            await s.close()


@pytest_asyncio.fixture(scope="function")
async def test_user(session):
    import bcrypt

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8"),
        status="approved",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user_pending(session):
    import bcrypt

    user = User(
        username="pendinguser",
        email="pending@example.com",
        password_hash=bcrypt.hashpw(b"testpass123", bcrypt.gensalt()).decode("utf-8"),
        status="pending",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def another_user(session):
    import bcrypt

    user = User(
        username="anotheruser",
        email="another@example.com",
        password_hash=bcrypt.hashpw(b"anotherpass123", bcrypt.gensalt()).decode("utf-8"),
        status="approved",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def client(session, test_user):
    """Provide an HTTP test client with userId cookie."""
    import main

    # Mock init_db to avoid PostgreSQL connection at startup
    main.init_db = lambda: None

    from database.db import get_db

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    # Set userId cookie on client
    cookies = {"userId": str(test_user.id)}
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as ac:
        yield ac

    app.dependency_overrides.clear()
